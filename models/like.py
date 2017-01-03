from google.appengine.ext import db
from render import render_str
from models.user import User, users_key
from models.post import Post, blog_key


# ## Comment model ##
def like_key(name='Likes'):
    """parent key of comment modle

    Args:
        name (str): equal to 'Post'

    Return:
        the parent path of Comment Model
    """
    return db.Key.from_path('comment', name)


class Like(db.Model):
    """A Like class contains certain pieces of information
    of each like from the DB Model

    Attr:
        user (User): the user.
        post (str): the post.

    """
    user = db.ReferenceProperty(User,
                                collection_name='like_user_set',
                                required=True)
    post = db.ReferenceProperty(Post,
                                collection_name='like_post_set',
                                required=True)
