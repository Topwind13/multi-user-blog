
import random
import re
import hmac
import hashlib
from string import letters

# from rander import render_str, render_post
from handlers.handler import Handler
from models.user import User, users_key
from handlers.userHandlerFunction import login_required, valid_username,  valid_pwd, valid_email


# ## Sign up Handler ##
class Signup(Handler):
    """ sign up page handler"""

    def get(self):
        """Render to signup page"""

        self.render("signup.html")

    def post(self):
        """summit new user data to DB"""

        self.username = self.request.get('username').lower()
        self.pwd = self.request.get('pwd')
        self.verify_pwd = self.request.get('verify_pwd')
        self.email = self.request.get('email')
        have_errors = False
        params = dict(username=self.username,
                      email=self.email)
        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username"
            have_errors = True
        elif User.by_name(self.username):
            params['error_username'] = "That username is taken. Try another. "
            have_errors = True

        if not valid_pwd(self.pwd):
            params['error_pwd'] = "That's not a valid password"
            have_errors = True
        elif self.pwd != self.verify_pwd:
            params['error_verify_pwd'] = "Your passwords doesn't match"
            have_errors = True

        if self.email and not valid_email(self.email):
            params['error_email'] = "That's not a valid email"
            have_errors = True

        if have_errors:
            self.render('signup.html', **params)
        else:
            user = User.register(self.username, self.pwd, self.email)
            user.put()

            self.login(user)
            welcome_msg = 'Welcome, %s' % (self.username)
            self.redirect('/blog?welcome_msg=%s' % (welcome_msg))


# ## Login Handler ##
class Login(Handler):
    """Login handler"""
    def get(self):
        """Render to login page"""
        self.render("login.html")

    def post(self):
        """summit username and password,
        then check whether the username and password are matched with DB
        """

        username = self.request.get('username').lower()
        pwd = self.request.get('pwd')
        remember = self.request.get('remember')

        user = User.login(username, pwd)  # class
        if user:
            self.login(user, remember)  # cookie
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render("login.html", error=msg)


class Logout(Handler):
    """Logout handler"""
    @login_required
    def get(self):
        """logout from the website"""
        self.logout()
        self.redirect('/blog/login')
