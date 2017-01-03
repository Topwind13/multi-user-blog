
import random
import re
import hmac
import hashlib
from string import letters
from functools import wraps


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


# login required
def login_required(function):
    """Decorator function for login required pages."""

    @wraps(function)
    def wrapper(self, *args, **kw):
        """Redirect to main if user doesn't logged in. """

        if not self.user:
            return self.redirect('/blog/login')
        return function(self, *args, **kw)
    return wrapper
