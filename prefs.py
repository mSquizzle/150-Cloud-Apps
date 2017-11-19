import webapp2
from google.appengine.api import users

import models

class PrefsPage(webapp2.RequestHandler):
    def post(self):
        userprefs = models.get_userprefs()
        try:
            first_name = self.request.get('first_name')
            userprefs.first_name = first_name
            last_name = self.request.get('last_name')
            userprefs.last_name = last_name
            phone_number = self.request.get('phone_number')
            userprefs.phone_number = phone_number
            blood_type = self.request.get('blood_type')
            userprefs.blood_type = blood_type
            address_1 = self.request.get('address_1')
            userprefs.address_1 = address_1
            address_2 = self.request.get('address_2')
            userprefs.address_2 = address_2
            city = self.request.get('city')
            userprefs.city = city
            state = self.request.get('state')
            userprefs.state = state
            zip_code = self.request.get('zip_code')
            userprefs.zip_code = zip_code
            userprefs.email = users.get_current_user().email()
            userprefs.put()
        except ValueError:
            # User did somethin weird
            pass

        self.redirect('/')

application = webapp2.WSGIApplication([('/prefs', PrefsPage)],
                                      debug=True)