import jinja2
import os
import webapp2

from google.appengine.api import users


template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.getcwd()))


class EmailAdminPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = template_env.get_template('templates/emailadmin.html')
        context = {
            'user': user
        }
        self.response.out.write(template.render(context))


application = webapp2.WSGIApplication([('/emailadmin.html', EmailAdminPage)],
                                     debug=True)