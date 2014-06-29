import webapp2
import json
import time
from google.appengine.ext import db
from google.appengine.api import memcache

import Base
global_time = time.time()
def get_cache(updated = False, key = "top_posts"):
  posts = memcache.get(key)
  if posts is None or updated:
    global global_time
    global_time = time.time()
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created_time DESC")
    memcache.set(key, posts)
  return posts

class Post(db.Model):
  title = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created_time = db.DateTimeProperty(auto_now_add=True)
  def to_dict(self):
    return dict([(p, (unicode(getattr(self, p)) if p is not "created_time" else getattr(self, p).strftime("%c"))) for p in self.properties()])

class User(db.Model):
  username = db.StringProperty(required=True)
  password = db.StringProperty(required=True)
  email = db.StringProperty()
  created_time = db.DateTimeProperty(auto_now_add=True)

class Hw5Handler(Base.Handler):
  def get(self):
    user_id = self.request.cookies.get("user_id")
    if user_id:
      posts = get_cache()
      if self.request.url.endswith(".json"):
        self.response.headers['Content-Type'] = "application/json; charset=UTF-8"
        result = [json.dumps(p.to_dict()) for p in posts]
        self.response.out.write(json.dumps(result))
      else:
        execution_time = "%.1f" % (time.time() - global_time)
        self.render("index_hw3.html", posts=posts, execution_time=execution_time)
    else:
      self.redirect("/hw5/signup")

class Hw5SignupHandler(Base.SignupHandler):
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
        self.redirect("/hw5/welcome")
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
        self.redirect("/hw5/welcome")
      else:
        error_username = "This username has been taken."
        self.write_form(error_username, "", error_email, "", "", email)
    else:
      if error_password:
        self.write_form(error_username, error_password, "", error_email, username, email)
      else:
        self.write_form(error_username, error_password, error_verify, error_email, username, email)

class Hw5LogInHandler(Base.SignupHandler):
  def get(self):
    user_id = self.request.cookies.get("user_id")
    if user_id:
      user = User.get_by_id(int(user_id.split("|")[0]))
      self.redirect("/hw5/welcome")
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
        self.redirect("/hw5/welcome")
    else:
      error_match = "Username or Password should not be empty!"
      self.render("login.html", error_match = error_match)

class Hw5LogOutHandler(Base.SignupHandler):
  def get(self):
    self.response.delete_cookie("user_id")
    self.redirect("/hw5/signup")

class Hw5WelcomeHandler(Base.SignupHandler):
  def get(self):
    user_id = self.request.cookies.get("user_id")
    if user_id:
      user = User.get_by_id(int(user_id.split("|")[0]))
      self.render("signup_pass.html", username = user.username)
    else:
      self.redirect("/hw5/signup")

class Hw5NewpostHandler(Base.Handler):
  def form_render(self, title="", content="", error=""):
    self.render("post_form_hw3.html", title=title, content=content, error=error)
  def get(self):
    user_id = self.request.cookies.get("user_id")
    if user_id:
      self.form_render()
    else:
      self.redirect("/hw5/signup")
  def post(self):
    title = self.request.get("subject")
    content = self.request.get("content")

    if title and content:
      p = Post(title=title, content=content)
      key = p.put()
      get_cache(True)
      self.redirect("/hw5/%d" % key.id())
    else:
      self.form_render(title, content, "Bad")

class Hw5PostHandler(Base.Handler):
  def get(self, post_id):
    p = Post.get_by_id(int(post_id))
    if self.request.url.endswith(".json"):
      self.response.headers['Content-Type'] = "application/json; charset=UTF-8"
      self.response.out.write(json.dumps(p.to_dict()))
    else:
      get_cache(False, post_id)
      execution_time = "%.1f" % (time.time() - global_time)
      self.render("post_hw3.html", p=p, execution_time=execution_time)

class Hw5FlushHandler(Base.Handler):
  def get(self):
    memcache.flush_all()
    global global_time
    global_time = time.time()
    self.redirect('/hw5')
