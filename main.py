
import os
import webapp2
import jinja2
import re

from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog_entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self, blog_entries="", page=1, limit=5, g="" ,count=0, offset=0, prev_button=True, next_button=True):

        #remember you have to assign the variable or get request won't store the value
        page = self.request.get('page')

        if page and page.isdigit():
            page = int(page)
            offset = (page - 1) * 5
        else:
            page = 1

        if page == 1:
            offset = 0
            prev_button = False

        blog_entries = get_posts(limit, offset)

        #use count to make sure there are no blog entries on the page after the last page
        #offset=offset will leave a next button on the last page

        count = blog_entries.count(offset=offset + 5, limit=limit)
        if count == 0:
            next_button = False

        self.render("mainpage.html", g=g, count=count, blog_entries=blog_entries, page=page, prev_button=prev_button, next_button=next_button)

class NewPost(Handler):
    def render_newpost(self, title="", blog_entry="", error=""):
        self.render("newpost.html", title=title, blog_entry=blog_entry, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        blog_entry = self.request.get("blog_entry")

        if title and blog_entry:
            b = Blog(title = title, blog_entry = blog_entry)
            b.put()
            #have to turn b.key().id() into a string to use it with '/blog'
            self.redirect('/blog/%s' % str(b.key().id()))
        else:
            error = "Whoops, Make sure both fields are filled out!"
            self.render_newpost(title, blog_entry, error)

def get_posts(limit, offset):
    # TODO: query the database for posts, and return them

    posts = db.GqlQuery("SELECT * FROM Blog "
                    "ORDER BY created DESC "
                    "LIMIT %s OFFSET %s" % (limit, offset))
    return posts

class ViewPostHandler(Handler):
    def get(self, id):
        blog_entry = Blog.get_by_id(int(id), parent=None)
        error =""
        if not blog_entry:
            error = "Incorrect blog id!"
        return self.render("singlepost.html", blog_entry=blog_entry, error=error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ], debug=True)
