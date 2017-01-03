from google.appengine.ext import db
from handlers.userHandlerFunction import valid_pw, make_pw_hash


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
