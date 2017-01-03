from google.appengine.ext import db
from render import render_str
from models.user import User, users_key
from models.post import Post, blog_key


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
