from google.appengine.api import users
from google.appengine.ext import db

# todo - need to switch this so it reads from SQL instead of Keystore
class DonorUserPrefs(db.Model):
    tz_offset = db.IntegerProperty(default=0)
    first_name = db.StringProperty(default="")
    last_name = db.StringProperty(default="")
    phone_number = db.StringProperty(default="")
    email = db.StringProperty(default="")
    blood_type = db.StringProperty(default="")
    zip_code = db.StringProperty(default="")
    address_1 = db.StringProperty(default="")
    address_2 = db.StringProperty(default="")
    city = db.StringProperty(default="")
    state = db.StringProperty(default="")
    last_donation_date = db.DateProperty(default = None)
    eligibility_status = db.StringProperty(default="Unknown")
    notification_preference = db.StringProperty(default="email")
    receive_outreach = db.BooleanProperty(default=True)
    user_id = db.IntegerProperty()
    user = db.UserProperty(auto_current_user_add=True)

def get_userprefs(user_id=None):
    if not user_id:
        user = users.get_current_user()
        if not user:
            return None
        user_id = user.user_id()

    key = db.Key.from_path('DonorUserPrefs', user_id)
    userprefs = db.get(key)
    if not userprefs:
        userprefs = DonorUserPrefs(key_name=user_id)
    return userprefs