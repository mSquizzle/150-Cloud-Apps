from google.appengine.api import mail
from google.appengine.api import users

import webapp2
import json
import models
from string import Template

class EmailPage(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        success_message = "email failed"
        success = False
        if user:
            try:
                sender_address = user.email()
                email_body = self.request.get('email_body')
                email_address = self.request.get('send_address')
                email_subject = self.request.get('email_subject')
                missing_fields = []
                if not email_body:
                    missing_fields.append("email body")
                if not email_address:
                    missing_fields.append("email address")
                if not email_subject:
                    missing_fields.append("email subject")
                if len(missing_fields) > 0 :
                    success_message = "Missing "+",".join(missing_fields)
                else:
                    body = "<html><head></head><body><pre>{}</pre></body></html>".format(email_body)
                    # based off of book's user pref's code
                    pref = models.get_userpref_by_email(email_address)
                    if pref :
                        allowed_subs = dict(first_name=pref.first_name, last_name=pref.last_name)
                        body = Template(body).substitute(allowed_subs)
                        mail.send_mail(sender=sender_address,
                                       to=email_address,
                                       subject=email_subject,
                                       body=body,
                                       html=body)
                        success_message = "message sent!"
                        success = True
                    else :
                        success_message = "The email specified is not in our system. Please try again."
            except :
                success_message = "There was an error sending your email. Please try again at another time."
                pass
        self.response.headers['Content-Type'] = 'application/json'
        obj = {
            'success': success,
            'message': success_message
        }
        self.response.out.write(json.dumps(obj))

application = webapp2.WSGIApplication([('/sendemail', EmailPage)],debug=True)