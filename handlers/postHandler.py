from google.appengine.ext import db
import time

from handlers.handler import Handler
from models.post import Post, blog_key
from models.comment import Comment, comment_key
from handlers.userHandlerFunction import login_required
from models.like import Like, like_key
from handlers.likeHandler import count_like



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
        like = Like.all().filter('post =', post).filter('user =', self.user).get()
        total_like = count_like(post)

        # break a line of content and rander a post to post page
        post._render_text = post.content.replace('\n', '<br>')
        self.render('post.html', post=post, user=self.user, comments=comments, like=like, total_like=total_like)


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
