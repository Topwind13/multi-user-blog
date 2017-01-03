import time

from handlers.handler import Handler
from models.post import Post, blog_key
from models.comment import Comment, comment_key
from handlers.userHandlerFunction import login_required


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
