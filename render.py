import os
import jinja2


template_dir = os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    """Render jinja template with parameters to html string.

    Args:
        template (str): template name to render.
        **params: an arbitrary number of parameters to render.

    Returns:
        str: rendered string.
    """

    template_jinja = jinja_env.get_template(template)
    return template_jinja.render(params)


def render_post(response, post):
    """Function to write out post subject and content"""

    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)
