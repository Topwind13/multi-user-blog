from google.appengine.ext import db
from render import render_str
from models.user import User, users_key


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
