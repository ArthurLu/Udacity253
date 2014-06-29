import webapp2
from google.appengine.ext import db

import Base

class User(db.Model):
  username = db.StringProperty(required=True)
  password = db.StringProperty(required=True)
  email = db.StringProperty()
  created_time = db.DateTimeProperty(auto_now_add=True)

class Hw4Handler(Base.SignupHandler):
  def check_username(self, username):
    user = db.GqlQuery("SELECT * FROM User WHERE username = '%s'" % username)
    return user.count() is 0
  def get(self):
    cookie = self.request.cookies.get("user_id")
    if not cookie:
      self.write_form()
    else:
      [user_id, hash_id] = cookie.split("|")
      user = User.get_by_id(int(user_id))
      if Base.valid_pw(user.username, user.password, cookie):
        self.redirect("/hw4/welcome")
      else:
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
        self.redirect("/hw4/welcome")
      else:
        error_username = "This username has been taken."
        self.write_form(error_username, "", error_email, "", "", email)
    else:
      if error_password:
        self.write_form(error_username, error_password, "", error_email, username, email)
      else:
        self.write_form(error_username, error_password, error_verify, error_email, username, email)

class Hw4WelcomeHandler(Base.SignupHandler):
  def get(self):
    user_id = self.request.cookies.get("user_id")
    if user_id:
      user = User.get_by_id(int(user_id.split("|")[0]))
      self.render("signup_pass.html", username = user.username)
    else:
      self.redirect("/hw4/signup")

class Hw4LogInHandler(Base.SignupHandler):
  def get(self):
    user_id = self.request.cookies.get("user_id")
    if user_id:
      user = User.get_by_id(int(user_id.split("|")[0]))
      self.redirect("/hw4/welcome")
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
        self.redirect("/hw4/welcome")
    else:
      error_match = "Username or Password should not be empty!"
      self.render("login.html", error_match = error_match)

class Hw4LogOutHandler(Base.SignupHandler):
  def get(self):
    self.response.delete_cookie("user_id")
    self.redirect("/hw4/signup")


