import webapp2
import json
import time
from google.appengine.ext import db

import Base
class Page(db.Model):
  name = db.StringProperty(required=True)
  content = db.TextProperty(default="")
  created_time = db.DateTimeProperty(auto_now_add=True)
  def to_dict(self):
    return dict([(p, (unicode(getattr(self, p)) if p is not "created_time" else getattr(self, p).strftime("%c"))) for p in self.properties()])

class User(db.Model):
  username = db.StringProperty(required=True)
  password = db.StringProperty(required=True)
  email = db.StringProperty()
  created_time = db.DateTimeProperty(auto_now_add=True)

class History(db.Model):
  name = db.StringProperty(required=True)
  content = db.TextProperty()
  created_time = db.DateTimeProperty(auto_now_add=True)

def check_login(user_hash_id):
  if user_hash_id:
    user_id = user_hash_id.split("|")[0]
    user = User.get_by_id(int(user_id))
    if user and Base.valid_pw(user.username, user.password, user_hash_id):
      return True, user.username
    else:
      return False, None
  else:
    return False, None

class FinalHandler(Base.Handler):
  def get(self):
    login, username = check_login(self.request.cookies.get("user_id"))
    self.render("final.html", login = login, username = username)

class FinalSignupHandler(Base.SignupHandler):
  def check_username(self, username):
    user = db.GqlQuery("SELECT * FROM User WHERE username = '%s'" % username)
    return user.count() is 0
  def get(self):
    self.write_form()
  def post(self):
    username = self.request.get("username")
    password = self.request.get("password")
    verify = self.request.get("verify")
    email = self.request.get("email")

    error_username = "" if self.valid_username(username) else "That's not a valid username."
    error_password = "" if self.valid_password(password) else "That wasn't a valid password. At least three characters"
    error_email = "" if self.valid_email(email) else "That's not a valid email."
    error_verify = "" if password == verify else "Your passwords didn't match."

    if (not error_username) and (not error_password) and (not error_verify) and (not error_email):
      if self.check_username(username):
        user = User(username = username, password = password, email = email)
        user_key = user.put()
        user_hash_id = Base.make_pw_hash(username, password, str(user_key.id()))
        self.response.headers.add_header("Set-cookie", "user_id = %s; path = /" % user_hash_id)
        self.redirect("/final")
      else:
        error_username = "This username has been taken."
        self.write_form(error_username, "", error_email, "", "", email)
    else:
      if error_password:
        self.write_form(error_username, error_password, "", error_email, username, email)
      else:
        self.write_form(error_username, error_password, error_verify, error_email, username, email)

class FinalLoginHandler(Base.SignupHandler):
  def get(self):
    login, username = check_login(self.request.cookies.get("user_id"))
    if login:
      self.redirect("/final")
    else:
      self.render("login.html")
  def post(self):
    username = self.request.get("username")
    password = self.request.get("password")
    error_match = ""
    if username and password:
      users = db.GqlQuery("SELECT * FROM User WHERE username = '%s' AND password = '%s'" % (username, password))
      if users.count() is 0:
        error_match = "Username and Password do not match!"
        self.render("login.html", error_match = error_match)
      else:
        user = users.get()
        user_hash_id = Base.make_pw_hash(username, password, str(user.key().id()))
        self.response.headers.add_header("Set-cookie", "user_id = %s; path = /" % user_hash_id)
        self.redirect("/final")
    else:
      error_match = "Username or Password should not be empty!"
      self.render("login.html", error_match = error_match)

class FinalLogoutHandler(Base.SignupHandler):
  def get(self):
    self.response.delete_cookie("user_id")
    self.redirect("/final")

class FinalPageHandler(Base.Handler):
  def form_render(self, page_name="", page_content="", login=False, username="", v="0"):
    self.render("final_page.html", page_name=page_name, page_content=page_content, username=username, login=login, v=v)
  def get(self, page_name):
    page_name = page_name[1:]
    page = Page.get_by_key_name(page_name)
    login, username = check_login(self.request.cookies.get("user_id"))
    version = self.request.get("v")
    if version:
      history = db.GqlQuery("SELECT * FROM History WHERE ANCESTOR IS '%s' ORDER BY created_time DESC" % page.key())
      h = history[int(version)]
      self.form_render(page_name=h.name, page_content=h.content, username=username, login=login, v=version)
    else:
      if page:
        self.form_render(page_name=page.name, page_content=page.content, username=username, login=login)
      else:
        if login:
          self.redirect("/final/_edit/%s" % page_name)
        else:
          self.render("404.html", page_name = page_name)

class FinalEditHandler(Base.Handler):
  def form_render(self, page_name="", content="", error="", username="", v="0"):
    self.render("final_edit.html", page_name=page_name, content=content, error=error, username=username, v=v)
  def get(self, page_name):
    page_name = page_name[1:]
    login, username = check_login(self.request.cookies.get("user_id"))
    if login:
      version = self.request.get("v")
      page = Page.get_or_insert(page_name, name=page_name)
      if version:
        history = db.GqlQuery("SELECT * FROM History WHERE ANCESTOR IS '%s' ORDER BY created_time DESC" % page.key())
        h = history[int(version)]
        self.form_render(page_name=h.name, content=h.content, username=username, v=version)
      else:
        self.form_render(page_name=page_name, username=username, content=page.content)
    else:
      self.redirect("/final")
  def post(self, page_name):
    page_name = page_name[1:]
    content = self.request.get("content")
    if content:
      page = Page.get_or_insert(page_name, name=page_name, content=content)
      page.content = content
      history = History(parent=page.key(), name=page.name, content=content)
      history.put()
      if page.put():
        self.redirect("/final/%s" % page_name)
    else:
      login, username = check_login(self.request.cookies.get("user_id"))
      self.form_render(username = username, content = content, error = "It should not be empty!")

class FinalHistoryHandler(Base.Handler):
  def form_render(self, page_name="", history=[], username=""):
    self.render("final_history.html", page_name=page_name, history=enumerate(history), username=username)
  def get(self, page_name):
    page_name = page_name[1:]
    login, username = check_login(self.request.cookies.get("user_id"))
    if login:
      page = Page.get_by_key_name(page_name)
      if page:
        history = db.GqlQuery("SELECT * FROM History WHERE ANCESTOR IS '%s' ORDER BY created_time DESC" % page.key())
        self.form_render(page_name=page.name, history=history, username=username)
      else:
        self.redirect("/final")
    else:
      self.redirect("/final")
