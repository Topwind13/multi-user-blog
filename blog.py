import os
import webapp2
import jinja2
import random
import re
import hmac
import hashlib
from google.appengine.ext import db
from string import letters
from functools import wraps
import time

template_dir = os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    """Render jinja template with parameters to html string.

    Args:
        template (str): template name to render.
        **params: an arbitrary number of parameters to render.

    Returns:
        str: rendered string.
    """

    template_jinja = jinja_env.get_template(template)
    return template_jinja.render(params)


def render_post(response, post):
    """Function to write out post subject and content"""

    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)


# login
def login_required(function):
    """Decorator function for login required pages."""

    @wraps(function)
    def wrapper(self, *args, **kw):
        """Redirect to main if user doesn't logged in. """

        if not self.user:
            return self.redirect('/blog/login')
        return function(self, *args, **kw)
    return wrapper


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

# User
secret = 'topp'  # set the secret value


def hash_str(string):
    """hash string with secret value by hmac.

    Args:
        string (str): the string to hash.
    """

    return hmac.new(secret, string).hexdigest()


def make_secure_val(string):
    """set string and hash that string for securation

    Args:
        string (str): the string to hash.

    Return:
        str: return secure string with hash value which seperated by pipe(|)
    """

    return "%s|%s" % (string, hash_str(string))


def check_secure_val(hash_val):
    """Check the validation of hash value.

    Args:
        hash_val (str): hash value to check.

    Return:
        return the value of hash if it validate, otherwise return 'None'
    """

    val = hash_val.split('|')[0]
    if hash_val == make_secure_val(val):
        return val


def make_salt(length=5):
    """Random 5 digits of alphabet

    Args:
        length (int): a number of digits

    Return:
        the string of 5 digits alphabet.
    """

    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    """Making hashed password

    Args:
        name(str): username from user
        pw (str): password from user
        salt: salt to make hash more secure

    Return:
        return the string of salt and hashed password which seperated by comma
    """

    if not salt:
        salt = make_salt()
    hash_pw = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, hash_pw)


def valid_pw(name, pw, pw_hash):
    """valid whether password correct

    Args:
        name(str): username from user
        pw (str): password from user
        pw_hash (str): hashed password with salt

    Return:
        return True if the password correct
    """

    salt = pw_hash.split(',')[0]
    return pw_hash == make_pw_hash(name, pw, salt)


# Model


# ## User model ##
def users_key(group='default'):
    """parent key of User modle

    Args:
        group (str): equal to 'default'

    Return:
        the parent path of User Model
    """

    return db.Key.from_path('users', group)


class User(db.Model):
    """A User class contains certain pieces of information
    of each user from the DB Model

    Attr:
        name (str): the username.
        pw_hash (str): hashed password.
        email (str): the email of user

    """
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        """Find user by id and return User instance

        Args:
            uid (int): User's id

        Returns:
            return User instance if it exists, otherwise return 'None'
        """

        return cls.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        """Find user by name and return User instance

        Args:
            name (str): User's username

        Returns:
            return User instance if it exists, otherwise return 'None'
        """
        return cls.all().filter('name =', name).get()

    @classmethod
    def register(cls, name, pw, email=None):
        """Make the User instance as provided infomation

        Args:
            name (str): User's username
            pw (str):User's password
            email: User's email

        Returns:
            return User instance with hashed password
        """

        pw_hash = make_pw_hash(name, pw)
        return cls(parent=users_key(),
                   name=name,
                   pw_hash=pw_hash,
                   email=email)

    @classmethod
    def login(cls, name, pw):
        """Find user by name and check the password whether it correct

        Args:
            name (str): User's username
            pw (str):User's password

        Returns:
            return User instance if user exists and password is matched
        """
        user = cls.by_name(name)
        if user and valid_pw(name, pw, user.pw_hash):
            return user


# ## Post model ##
def blog_key(name='default'):
    """parent key of blog modle

    Args:
        name (str): equal to 'default'

    Return:
        the parent path of Post Model
    """

    return db.Key.from_path('blogs', name)


class Post(db.Model):
    """A Post class contains certain pieces of information
    of each post from the DB Model

    Attr:
        user (User): the user.
        subject (str): a subject of the post.
        content (text): a content of the post.
        created (datetime): created date and time of the post.
    """

    user = db.ReferenceProperty(User, collection_name='posts', required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        """rander function to the page"""

        self._render_text = self.content.replace('\n', '<br>')
        return render_str('post_template.html', post=self, user=self.user)


# ## Comment model ##
def comment_key(name='Post'):
    """parent key of comment modle

    Args:
        name (str): equal to 'Post'

    Return:
        the parent path of Comment Model
    """
    return db.Key.from_path('comment', name)


class Comment(db.Model):
    """A Comment class contains certain pieces of information
    of each comment from the DB Model

    Attr:
        user (User): the user.
        post (str): the post.
        content (text): a content of the post.
        created (datetime): created date and time of the post.

    """
    user = db.ReferenceProperty(User,
                                collection_name='comment_user_set',
                                required=True)
    post = db.ReferenceProperty(Post,
                                collection_name='comment_post_set',
                                required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self, post, user):
        """rander function to the page"""

        self._render_text = self.content.replace('\n', '<br>')
        return render_str('comment_template.html',
                          comment=self,
                          post=post,
                          user=user)


# ## blog post Handler ##
class BlogPage(Handler):
    """Blog Main page handler"""

    def get(self):
        """Get posts from database
        queried by created date and set the limit of posts per page
        render it to the page
        """

        page = self.request.get('page')
        if page:
            page = int(page)
        else:
            page = 1
        limit = 10
        offset = limit * (page - 1)
        posts = Post.all().order('-created').fetch(limit=limit, offset=offset)
        number_posts = Post.all().count()
        total_pages = number_posts / limit
        if number_posts % limit:
            total_pages += 1

        self.render('home.html', posts=posts, page=page,
                    total_pages=total_pages, user=self.user)


class MyPostPage(Handler):
    """list of posts page of login user handler"""

    @login_required
    def get(self):
        """Get posts of a user from database
        queried by created date and set the limit of posts per page
        render it to the page
        """

        page = self.request.get('page')
        if page:
            page = int(page)
        else:
            page = 1
        limit = 10
        offset = limit * (page - 1)

        my_posts = Post.all().order('-created').filter('user =', self.user)

        number_posts = my_posts.count()
        total_pages = number_posts / limit
        if number_posts % limit:
            total_pages += 1

        posts = my_posts.fetch(limit=limit, offset=offset)
        self.render('mypost.html', posts=posts, page=page,
                    total_pages=total_pages, user=self.user)


class NewPostPage(Handler):
    """New post page handler"""

    @login_required
    def get(self):
        """render new post form"""

        self.render("newpost.html", user=self.user)

    @login_required
    def post(self):
        """submit new post data to the database
        and redirecet to the post page
        """

        subject = self.request.get('subject')
        content = self.request.get('content')

        have_errors = False

        if not subject:
            error_subject = "Please write down the subject"
            have_errors = True
        if not content:
            error_content = "Content is required"
            have_errors = True

        if have_errors:
            self.render("newpost.html",
                        subject=subject,
                        content=content,
                        error_subject=error_subject,
                        error_content=error_content,
                        user=self.user)
        else:
            post = Post(parent=blog_key(),
                        subject=subject,
                        content=content,
                        user=self.user)
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))


class PostPage(Handler):
    """Post page handler"""

    def get(self, post_id):
        """get post's id and rander it to the page
        Args:
            post_id (str): Post's id

        """
        post = Post.get_by_id(int(post_id), parent=blog_key())
        if not post:
            self.error(404)
            return

        # comment query object
        comments = Comment.all().filter('post =', post).order('created')

        # break a line of content and rander a post to post page
        post._render_text = post.content.replace('\n', '<br>')
        self.render('post.html', post=post, user=self.user, comments=comments)


class EditPostPage(Handler):
    """Edit post page handler"""

    @login_required
    def get(self, post_id):
        """get post's id and rander it to edit page of that post
        Args:
            post_id (str): Post's id
        """

        post = Post.get_by_id(int(post_id), parent=blog_key())

        if post and self.user.key().id() == post.user.key().id():
            self.render("edit.html", post=post, user=self.user)
        else:
            self.redirect('/blog/%s' % str(post.key().id()))

    @login_required
    def post(self, post_id):
        """resummit the post data to DB and rander it the post page
        Args:
            post_id (str): Post's id

        """
        post = Post.get_by_id(int(post_id), parent=blog_key())

        if post and self.user.key().id() == post.user.key().id():
            post.subject = self.request.get('subject')
            post.content = self.request.get('content')

            # initialize error to false
            have_errors = False

            # if there is no subject or content, it will throw errors
            if not post.subject:
                error_subject = "Please write down the subject"
                have_errors = True
            if not post.content:
                error_content = "Content is required"
                have_errors = True

            if have_errors:
                self.render("edit.html",
                            subject=post.subject,
                            content=post.content,
                            error_subject=error_subject,
                            error_content=error_content,
                            user=self.user)
            else:
                post.put()
                self.redirect('/blog/%s' % str(post.key().id()))


class CancelEdit(Handler):
    """Cancel edit post page handler"""\

    def get(self, post_id):
        """get post's id and rander it to post page
        Args:
            post_id (str): Post's id
        """
        post = Post.get_by_id(int(post_id), parent=blog_key())
        self.redirect('/blog/%s' % str(post.key().id()))


class DeletePost(Handler):
    """Delete post page handler"""

    @login_required
    def get(self, post_id):
        """delete new post from DB
        Args:
            post_id (str): Post's id

        """
        post = Post.get_by_id(int(post_id), parent=blog_key())

        if post and self.user.key().id() == post.user.key().id():
            comments = Comment.all().filter('post =', post)
            db.delete(comments)
            post.delete()

        time.sleep(0.2)
        self.redirect('/blog')


# ## Comment Handler ##
class NewComment(Handler):
    """New comment handler"""

    @login_required
    def post(self):
        """summit a comment to DB and rander it the post page"""
        post_id = self.request.get('post_id')
        post = Post.get_by_id(int(post_id), parent=blog_key())
        content = self.request.get('comment')

        if content:
            comment = Comment(parent=comment_key(),
                              content=content,
                              user=self.user,
                              post=post)
            comment.put()

        time.sleep(0.1)
        self.redirect('/blog/%s' % str(post.key().id()))


class EditComment(Handler):
    """Edit comment handler"""

    @login_required
    def post(self):
        """resummit the comment data to DB and rander it the post page"""
        comment_id = self.request.get('comment_id')
        post_id = self.request.get('post_id')
        comment = Comment.get_by_id(int(comment_id), parent=comment_key())
        post = Post.get_by_id(int(post_id), parent=blog_key())
        if comment and self.user.key().id() == comment.user.key().id():
            comment.content = self.request.get('content')

            have_errors = False

            if not comment.content:
                error_content = "Content is required"
                have_errors = True

            if have_errors:
                self.render("edit_comment.html",
                            comment=comment,
                            error_content=error_content,
                            user=self.user)
            else:
                comment.put()
                time.sleep(0.1)

        self.redirect('/blog/%s' % str(post.key().id()))


class DeleteComment(Handler):
    """Delete comment handler"""

    @login_required
    def post(self, comment_id):
        """delete new post from DB
        Args:
            comment_id (str): Comment's id

        """
        comment = Comment.get_by_id(int(comment_id), parent=comment_key())
        if comment and self.user.key().id() == comment.user.key().id():
            comment.delete()
            time.sleep(0.1)

        self.redirect('/blog/%s' % str(comment.post.key().id()))


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


def valid_username(username):
    """validation of username

    Args:
        username (str): User's username

    Return:
        return 'true' if it valid
    """

    RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return RE.match(username)


def valid_pwd(pwd):
    """validation of password

    Args:
        password (str): User's password

    Return:
        return 'true' if it valid
    """
    RE = re.compile(r"^.{3,20}$")
    return RE.match(pwd)


def valid_email(email):
    """validation of email

    Args:
        email (str): User's email

    Return:
        return 'true' if it valid
    """
    RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
    return RE.match(email)


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


class MainPage(Handler):
    """MainPage handler"""
    def get(self):
        self.redirect('/blog')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogPage),
                               ('/blog/newpost', NewPostPage),
                               ('/blog/mypost', MyPostPage),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ('/blog/([0-9]+)/edit', EditPostPage),
                               ('/blog/([0-9]+)/cancel_edit', CancelEdit),
                               ('/blog/new_comment', NewComment),
                               ('/blog/edit_comment', EditComment),
                               ('/blog/delete_comment/([0-9]+)', DeleteComment),
                               ('/blog/signup', Signup),
                               ('/blog/login', Login),
                               ('/blog/logout', Logout),
                               ],
                              debug=True)
