import webapp2
nam

import Base

class Post(db.Model):
  title = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created_time = db.DateTimeProperty(auto_now_add=True)

class Hw3Handler(Base.Handler):
  def get(self):
    post = db.GqlQuery("SELECT * FROM Post ORDER BY created_time DESC")
    self.render("index_hw3.html", post=post)

class Hw3NewpostHandler(Base.Handler):
  def form_render(self, title="", content="", error=""):
    self.render("post_form_hw3.html", title=title, content=content, error=error)
  def get(self):
    self.form_render()
  def post(self):
    title = self.request.get("subject")
    content = self.request.get("content")

    if title and content:
      p = Post(title=title, content=content)
      key = p.put()
      self.redirect("/hw3/%d" % key.id())
    else:
      self.form_render(title, content, "Bad")

class Hw3PostHandler(Base.Handler):
  def get(self, post_id):
    p = Post.get_by_id(int(post_id))
    self.render("post_hw3.html", p=p)