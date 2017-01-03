import os
import webapp2

from handlers.handler import Handler
from handlers.postHandler import BlogPage, NewPostPage, MyPostPage, PostPage, DeletePost, EditPostPage, CancelEdit
from handlers.commentHandler import NewComment, EditComment, DeleteComment
from handlers.userAuthHandler import Signup, Login, Logout


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
