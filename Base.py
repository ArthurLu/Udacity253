import webapp2
import jinja2
import re
import os
import hashlib

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(user_name, user_pw, user_id):
    return "%s|%s" % (user_id, hashlib.sha256(user_name + user_pw + user_id).hexdigest())

def valid_pw(user_name, user_pw, h):
    [user_id, pw_hash] = h.split("|")
    return hashlib.sha256(user_name + user_pw + user_id).hexdigest() == pw_hash

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class SignupHandler(Handler):
    def write_form(self, error_username="", error_password="", error_verify="", error_email="", username="", email=""):
        self.render("signup.html",
                    error_email = error_email,
                    error_username = error_username,
                    error_password = error_password,
                    error_verify = error_verify,
                    username = username,
                    email = email)
    def valid_username(self, username):
        return USER_RE.match(username)
    def valid_password(self, password):
        return PASSWORD_RE.match(password)
    def valid_email(self, email):
        if email:
            return EMAIL_RE.match(email)
        else:
            return True


