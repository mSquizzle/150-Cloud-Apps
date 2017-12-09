import datetime
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

class TimeSlot(ndb.Model):
    user_id = ndb.StringProperty()
    start_time = ndb.DateTimeProperty(required=True)
    can_be_scheduled = ndb.BooleanProperty(default=True)
    event = ndb.KeyProperty(kind=Event, required=True)
    location = ndb.StringProperty()
    notes = ndb.StringProperty()
    scheduled_for_deletion = ndb.BooleanProperty(default=False)

# need utilities for this
def list_events(limit=10):
    q = Event.query().order(Event.end_date).order(Event.start_date)\
        .filter(Event.end_date > datetime.datetime.now())\
        .filter(Event.scheduled_for_deletion==False)#.filter(Event.published==True)
    return q.fetch(limit)

def list_open_slots(event):
    if event:
        q = TimeSlot.query().filter(TimeSlot.event == event.key)\
            .filter(TimeSlot.can_be_scheduled == True)\
            .filter(TimeSlot.scheduled_for_deletion == False)\
            .filter(TimeSlot.start_time > datetime.datetime.now())
        return q.fetch()
    return None
