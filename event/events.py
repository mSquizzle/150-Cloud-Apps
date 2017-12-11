import datetime
import pytz
from google.appengine.ext import ndb

class Event(ndb.Model):
    inst_id = ndb.StringProperty(required=True)
    location = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    num_parallel = ndb.IntegerProperty(required=True, default=1)
    apt_slot = ndb.IntegerProperty(required=True, default=15)
    last_updated = ndb.DateTimeProperty(auto_now=True)
    published = ndb.BooleanProperty(default=False)
    start_date = ndb.DateTimeProperty(required=True)
    end_date = ndb.DateTimeProperty(required=True)
    scheduled_for_deletion = ndb.BooleanProperty(default=False)

def formatted_start_date(event):
    event.start_date.strftime("%B %d, %Y at %I:%M %p")

def get_as_eastern(utc_date):
    utc_date = utc_date.replace(tzinfo=pytz.timezone("UTC"))
    return utc_date.astimezone(tz=pytz.timezone("US/Eastern"))

class TimeSlot(ndb.Model):
    user_id = ndb.StringProperty()
    start_time = ndb.DateTimeProperty(required=True)
    can_be_scheduled = ndb.BooleanProperty(default=True)
    event = ndb.KeyProperty(kind=Event, required=True)
    location = ndb.StringProperty()
    notes = ndb.TextProperty()
    scheduled_for_deletion = ndb.BooleanProperty(default=False)
    notified = ndb.BooleanProperty(required=True, default=False)

# need utilities for this
def list_events(limit=10):
    q = Event.query().order(Event.end_date).order(Event.start_date)\
        .filter(Event.end_date > datetime.datetime.now())\
        .filter(Event.scheduled_for_deletion==False)\
        .filter(Event.published==True)
    return q.fetch(limit)

def list_configured_events(id,limit=10, offset=0):
    q = Event.query().order(-Event.end_date)\
        .filter(Event.scheduled_for_deletion == False)\
        .filter(Event.inst_id == str(id))
    return q.fetch(limit, offset=offset)

def count_configured_events(id):
    q = Event.query().order(-Event.end_date) \
        .filter(Event.scheduled_for_deletion == False)\
        .filter(Event.inst_id == str(id))
    return q.count()

def list_open_slots(event):
    if event:
        q = TimeSlot.query().filter(TimeSlot.event == event.key)\
            .filter(TimeSlot.can_be_scheduled == True) \
            .filter(TimeSlot.user_id == None) \
            .filter(TimeSlot.scheduled_for_deletion == False)\
            .filter(TimeSlot.start_time > datetime.datetime.now())\
            .order(TimeSlot.start_time)
        return q.fetch()
    return None

def get_time_slot(tsid, eid):
    apt_long = int(tsid)
    parent_key = ndb.Key(Event, int(eid))
    time_slot = TimeSlot.get_by_id(apt_long, parent=parent_key)
    return time_slot

def get_events_to_notify():
    q = Event.query().filter(Event.start_date > datetime.datetime.now())\
        .filter(Event.start_date < (datetime.datetime.now()+datetime.timedelta(days=1)))\
        .filter(Event.published == True).filter(Event.scheduled_for_deletion == False)
    return q