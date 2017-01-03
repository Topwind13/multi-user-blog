# [Multi User Blog Project](https://github.com/Topwind13/multi-user-blog)
Multi User Blog is the project which is a part of [Udacity Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)


## Technology
* HTML 5
* CSS
* JavaScript
* jQuery
* Python
* Goole App Engine

## Features
* [live version](https://multi-user-blog-154519.appspot.com/blog)
* Front page that lists blog posts.
* A form to submit new entries.
* Blog posts have their own page.
* Have a registration form that validates user input, and displays the errors when necessary.
* After a successful registration, a user is directed to a welcome page with a greeting user.
*  Store passwords securely.
* Have a login form that validates user input, and displays the errors when necessary.
* After a successful login, the user is directed to the same welcome page.
* logout features
* Users should only be able to edit/delete their posts. They receive an error message if they disobey this rule.
* Users can comment on posts. They can only edit/delete their own posts, and they should receive an error message if they disobey this rule.


## HTML and CSS template
Multi User blog was created by using [clean-blog template](http://startbootstrap.com/template-overviews/clean-blog/), which provided by **[David Miller](http://davidmiller.io/)**, Owner of [Blackrock Digital](http://blackrockdigital.io/).

## Run in localhost
you need to install [Python](https://www.python.org/downloads/) and [Google App Engine SDK](https://cloud.google.com/appengine/docs/python/download).
If you've already installed them, clone the repo and run the project

    $ git clone https://github.com/Topwind13/multi-user-blog
    $ cd multi-user-blog
    $ dev_appserver.py .

you can visit the application at this URL: `http://localhost:8080`.

and access to database at this URL: `http://localhost:8000/datastore`.

you can quit your localhost: `ctrl+c`

## Contributor
**[Topp, Pongsakorn Tikapichart](https://github.com/Topwind13)**

## Copyright and License

Copyright 2017 MultiUserBlog By TOPP.  Code released under the [MIT](https://github.com/Topwind13/multi-user-blog/blob/master/LICENSE) license.
