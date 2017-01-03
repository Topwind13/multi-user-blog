import webapp2
import time

from userHandlerFunction import check_secure_val, make_secure_val
from models.user import User, users_key
from render import render_str



# ## Handler ##
class Handler(webapp2.RequestHandler):
    """A base blog handler class provides functions used in the pages"""

    def write(self, *args, **kwargs):
        """To write to browser, which is the instance fucntion of response.out.write

        Args:
            *args: an arbitrary number of arguments
            **kwargs: an arbitrary number of keyward arguments
        """

        self.response.out.write(*args, **kwargs)

    def render(self, template, **kwargs):
        """Render to browser

        Args:
            template (str): template name to render.
            **kwargs: an arbitrary number of keyward arguments
        """

        self.write(render_str(template, **kwargs))

    def set_secure_cookie(self, name, val, remember):
        """Set secure cookie to a browser

        Args:
            name (str): cookie name.
            val (str): cookie value.
            remember(str/boolean): the string value or false
            to set longer cookie.
        """

        cookie_val = make_secure_val(val)
        cookie_str = '%s=%s; Path=/;' % (name, cookie_val)
        if remember:
            expires = time.time() + 5000 * 24 * 3600  # 5000 days from now
        else:
            expires = time.time() + 24 * 3600
        expires_str = time.strftime("%a, %d-%b-%Y %T GMT",
                                    time.gmtime(expires))
        expires_date = 'expires= %s;' % expires_str
        cookie_str += expires_date
        self.response.headers.add_header('Set-Cookie', cookie_str)

    def read_secure_cookie(self, name):
        """read secure cookie value and check validation

        Args:
            name (str): cookie name.

        Returns:
            str or False: the cookie value if it valid,
            otherwise return 'false'
        """

        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user, remember=False):
        """set cookie value to the browser

        Args:
            user (User): user instance to login.
            remember(str/boolean): set to remember cookie longer.
            If there is not value, the default would be 'false'
        """

        self.set_secure_cookie('user_id', str(user.key().id()), remember)

    def logout(self):
        """remove cookie value from the browser"""

        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """set user from cookie value if exist"""

        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
