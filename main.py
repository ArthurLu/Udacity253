#
import webapp2

import Base
import HW2
import HW3
import HW4
import HW5
import Final

class MainHandler(Base.Handler):
    def get(self):
        self.render("index.html")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/hw2', HW2.Hw2Handler),
    ('/hw2/signup', HW2.Hw2SignupHandler),
    ('/hw2/welcome', HW2.Hw2WelcomeHandler),
    ('/hw3', HW3.Hw3Handler),
    ('/hw3/newpost', HW3.Hw3NewpostHandler),
    ('/hw3/(\d+)', HW3.Hw3PostHandler),
    ('/hw4/signup', HW4.Hw4Handler),
    ('/hw4/login', HW4.Hw4LogInHandler),
    ('/hw4/logout', HW4.Hw4LogOutHandler),
    ('/hw4/welcome', HW4.Hw4WelcomeHandler),
    ('/hw5/?(?:\.json)?', HW5.Hw5Handler),
    ('/hw5/signup', HW5.Hw5SignupHandler),
    ('/hw5/login', HW5.Hw5LogInHandler),
    ('/hw5/logout', HW5.Hw5LogOutHandler),
    ('/hw5/welcome', HW5.Hw5WelcomeHandler),
    ('/hw5/(\d+)(?:\.json)?', HW5.Hw5PostHandler),
    ('/hw5/newpost', HW5.Hw5NewpostHandler),
    ('/hw5/flush', HW5.Hw5FlushHandler),
    ('/final/?', Final.FinalHandler),
    ('/final/signup/?', Final.FinalSignupHandler),
    ('/final/login/?', Final.FinalLoginHandler),
    ('/final/logout/?', Final.FinalLogoutHandler),
    ('/final/_edit' + Base.PAGE_RE, Final.FinalEditHandler),
    ('/final/_history' + Base.PAGE_RE, Final.FinalHistoryHandler),
    ('/final' + Base.PAGE_RE, Final.FinalPageHandler)], debug=True)
