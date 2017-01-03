import time

from handlers.handler import Handler
from models.post import Post, blog_key
from models.like import Like, like_key
from handlers.userHandlerFunction import login_required


# ## like Handler ##
class NewLike(Handler):
    """New like handler"""

    @login_required
    def post(self):
        """summit a like to DB"""
        post_id = self.request.get('post_id')
        post = Post.get_by_id(int(post_id), parent=blog_key())
        if self.user.key().id() != post.user.key().id():
            liked = Like.all().filter('post =', post).filter('user =', self.user).get()
            if not liked:
                like = Like(parent=like_key(),
                            user=self.user,
                            post=post)
                like.put()
                time.sleep(0.1)
        self.redirect('/blog/%s' % str(post.key().id()))


class Unlike(Handler):
    """Unlike handler"""

    @login_required
    def post(self):
        """delete like post from DB
        Args:
            like_id (str): Like's id

        """
        like_id = self.request.get('like_id')
        like = Like.get_by_id(int(like_id), parent=like_key())
        if like and self.user.key().id() == like.user.key().id():
            like.delete()
            time.sleep(0.1)

        self.redirect('/blog/%s' % str(like.post.key().id()))

def count_like(post):
    return Like.all().filter('post =', post).count()
