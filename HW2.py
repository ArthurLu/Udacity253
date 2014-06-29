#Hw2
import webapp2
import re

import Base

def ROT13(c):
  num = ord(c)
  if num >= 97 and num <= 122:
    num += 13
    return chr(num - 26) if num > 122 else chr(num)
  elif num >= 65 and num <= 90:
    num += 13
    return chr(num - 26) if num > 90 else chr(num)
  else:
    return c

class Hw2Handler(Base.Handler):
  def get(self):
    self.render("hw2.html", text = '')
  def post(self):
    text = self.request.get("text")
    result = ""
    for c in text:
      result += ROT13(c)
    self.render("hw2.html", text = result)

class Hw2SignupHandler(Base.SignupHandler):
  def get(self):
    self.write_form()
  def post(self):
    username = self.request.get("username")
    password = self.request.get("password")
    verify = self.request.get("verify")
    email = self.request.get("email")
    error_username = "" if self.valid_username(username) else "That's not a valid username."
    error_password = "" if self.valid_password(password) else "That wasn't a valid password."
    error_email = "" if self.valid_email(email) else "That's not a valid email."
    error_verify = "" if password == verify else "Your passwords didn't match."
    if (not error_username) and (not error_password) and (not error_verify) and (not error_email):
      self.redirect("/hw2/welcome?username=" + username)
    else:
      if error_password:
        self.write_form(error_username, error_password, error_email, "", username, email)
      else:
        self.write_form(error_username, error_password, error_verify, error_email, username, email)

class Hw2WelcomeHandler(Base.Handler):
  def get(self):
    username = self.request.get("username")
    self.render("signup_pass.html", username = username)


