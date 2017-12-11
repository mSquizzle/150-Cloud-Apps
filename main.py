import os, re, datetime, urllib, requests, logging
from functools import wraps, partial
import requests
from google.appengine.api import mail
from requests_toolbelt.adapters import appengine
from google.appengine.api import users
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, url_for, flash, \
        session, g, redirect, abort, Response
import datetime
import urllib
from google.appengine.ext import ndb
from google.appengine.api import app_identity, mail
import json
from event import events, create, update
from string import Template
from forms import login, institution, donor, radius, eligibility, email, settings
from event import events, create, update

app = Flask (__name__)
app.config.from_pyfile('./config.py')

appengine.monkeypatch()

class Alert:
    """
    Bootstrap style classes used for flashing messages to the client.
    Sets the category of the message which is processed in the skeleton
    template.
    """
    success = "alert-success"
    info = "alert-info"
    warning = "alert-warning"
    danger = "alert-danger"


def get_db():
    """
    Lazy-load function that makes a connection to the database. The connection
    is configured to autocommit changes and is automatically closed at the end
    of the request by the close_db function.
    """
    if not hasattr(g, 'connection'):
        g.connection = app.config['CONNECT']()
    return g.connection

def get_maps_key():
    key = os.environ.get('MAPS_KEY')
    return key

def get_mce_key():
    key = os.environ.get('MCE_KEY')
    return key

def get_zipcode_key():
    return '7FhkHmuRBeyrwzqsdnBqZQEJTXVOekSakAs9zD226ePAcfxCT3TypBriarNbaYyW'

def get_id():
    id = app_identity.get_application_id()
    if not id:
        id = os.environ.get('PROJECT_ID')
    logging.info(os.environ.get('PROJECT_ID'))
    return id

def get_current_time():
    return datetime.datetime.now()

# TODO: handle possibility of being logged in as both user types
@app.before_request
def authenticate():
    """
    Checks if the user is authenticated. Abstracts over the differences
    between donor and institutional accounts and stores important variables
    in the application context ("g") which is accessible from within the
    template rendering context.
    """
    def unauthenticated():
        g.authenticated = False
        g.individual_login = users.create_login_url(redirect_url())
        g.institution_login = url_for('inst_login')

    user = users.get_current_user()
    # check if session is already authenticated
    if session.get("authenticated"):
        g.authenticated = True
        g.account_type = session.get("account_type")
        g.account_id = session.get("account_id")
        if g.account_type == "donor":
            g.logout = users.create_logout_url(url_for('index'))
        else:
            g.logout = url_for('logout')
    # if donor just finished creating an account then
    # do not serve the complete_account page
    elif user and hasattr(request.url_rule, 'rule') and url_for('complete_individual') in request.url_rule.rule:
        unauthenticated()
        return
    # check for donor account
    elif user:
        cursor = get_db().cursor()
        cursor.execute(
            "SELECT id FROM donor WHERE email = %s",
            (user.email(),)
        )
        row = cursor.fetchone()
        if row:
            g.authenticated = True
            g.account_type = 'donor'
            g.account_id = row[0]
            g.logout = users.create_logout_url(url_for('index'))
        else:
            unauthenticated()
            # account not finished, redirect to form
            form = donor.Form()
            return render_template(
                'accounts/complete_account.html',
                form=form
            )
    else:
        unauthenticated()
    
@app.teardown_appcontext
def close_db(error):
    """
    Closes the database at the end of the request if it has been opened.
    """
    if g.get('connection'):
        g.connection.close()

def redirect_url(default='index'):
    """
    Helper function which chooses a url to redirect the client to.
    """
    return request.args.get('next') or \
        request.referrer or \
        url_for(default)

def report_errors(err):
    """
    Reports form errors by flashing them to the client. If there are multiple
    errors for a given field then it only reports the first.
    """
    for field_name, field_errors in err.iteritems():
        flash(field_errors[0], Alert.warning)

def login_required(func):
    """
    Decorator that ensures client is authenticated. Returns HTTP status 401
    if unathenticated.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get("authenticated"):
            abort(401)
        return func(*args, **kwargs)
    return decorated_view

def _required(func, group):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not g.get("authenticated") or g.get("account_type") not in group:
            abort(401)
        return func(*args, **kwargs)
    return decorated_view

donor_required = partial(_required, group=["donor"])

bank_required = partial(_required, group=["bank"])

hospital_required = partial(_required, group=["hospital"])

institution_required = partial(_required, group=["hospital", "bank"])

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(404)
def unauthorized(e):
    return render_template('404.html'), 404

################################################################################
#                                  Routing                                     #
################################################################################

@app.route('/')
def index():
    upcoming_events = events.list_events()
    event_list = []
    for event in upcoming_events:
        date = events.get_as_eastern(event.start_date)
        event_list.append({
            'location' : event.location,
            'date': date.strftime("%B %d, %Y at %I:%M %p"),
            'start_date' : event.start_date,
            'end_date' : event.end_date,
            'key' : event.key
        })
    return render_template('index.html', event_list=event_list, current_time=get_current_time())


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/account/choose-account')
def choose_account():
    return render_template('accounts/choose-account.html')


@app.route('/account/create-account', methods=['GET', 'POST'])
def create_account():
    """
    Create a blood bank or hospital admin account.
    """
    form = institution.Form()
    if form.validate_on_submit():
        cursor = get_db().cursor()
        cursor.execute(
            "INSERT INTO {} (hashed, name, phone, email, zipcode)"
            "VALUES (%s, %s, %s, %s, %s)".format(form.institution.data),
            (generate_password_hash(form.password.data),
            form.name.data, "phone", form.email.data, 1111)
        )
        flash("Successfully created acount", Alert.success)
        return redirect(url_for('inst_login'))
    elif form.errors:
        report_errors(form.errors)
    form.institution.data = request.args.get("inst")
    return render_template(
        'accounts/create-account.html',
        form=form
    )


@app.route('/account/complete-individual', methods=['POST'])
def complete_individual():
    form = donor.Form()
    user = users.get_current_user()
    if form.validate_on_submit():
        cursor = get_db().cursor()
        cursor.execute(
            "INSERT INTO donor"
            "(first_name, last_name, phone, zipcode, email)"
            "VALUES (%s, %s, %s, %s, %s)",
            (form.first_name.data, form.last_name.data, form.phone.data, "{:05d}".format(form.zipcode.data), user.email())
        )
        flash("Successfully created acount!", Alert.success)
        return redirect(url_for('index'))
    report_errors(form.errors)
    return render_template(
        'accounts/complete_account.html',
        form=form
    )


@app.route('/account/login', methods=['GET', 'POST'])
def inst_login():
    form = login.Form()
    if form.validate_on_submit():
        cursor = get_db().cursor()
        cursor.execute(
            "SELECT id, hashed FROM {} WHERE email=%s;".format(form.institution.data),
            (form.email.data,)
        )
        row = cursor.fetchone()
        if not row:
            flash(
                'Unable to find account under email "{}"'.format(form.email.data),
                Alert.warning
            )
        elif check_password_hash(row[1], form.password.data):
            session['authenticated'] = True
            session['account_type'] = form.institution.data
            session['account_id'] = row[0]
            return redirect(url_for('index'))
        else:
            flash('Invalid password', Alert.warning)
    report_errors(form.errors)
    return render_template(
        'accounts/login.html',
        form=form
    )


@app.route('/account/logout')
def logout():
    """
    Invalidate institution from the session and redirect to homepage.
    """
    session.pop('authenticated', None)
    session.pop('account_type', None)
    session.pop('account_id', None)
    return redirect(url_for('index'))


@app.route('/settings', methods=["GET", "POST"])
@donor_required
def update_settings():
    form = settings.Form()
    cursor = get_db().cursor()
    if form.validate_on_submit():
        cursor.execute(
            "UPDATE donor SET contact=%s, outreach=%s WHERE id=%s",
            (form.contact.data, form.outreach.data, g.account_id)
        )
        flash("Donor settings updated", Alert.success)
    report_errors(form.errors)
    cursor.execute("SELECT contact, outreach FROM donor WHERE id=%s", (g.account_id,))
    row = cursor.fetchone()
    form.contact.data = row[0]
    form.outreach.data = row[1]
    return render_template('settings.html', form=form)


@app.route('/emailadmin', methods=['GET', 'POST'])
@bank_required
def emailadmin():
    form = email.Form()
   # sender_address = email address associated with login
    success = False
    if form.validate_on_submit():
	url = "https://www.zipcodeapi.com/rest/{key}/radius.json/{zipcode}/{distance}/miles?minimal".format(key=get_zipcode_key(), \
	   zipcode='{:05d}'.format(form.zipcode.data),\
	   distance='{:03d}'.format(form.radius.data))
	
	response = requests.get(url)
  	decoded = json.loads(response.text)
	zipcode_string = str(decoded)
	formatted_zipcode = zipcode_string.replace("u'",'').replace("'",'')\
	    .replace('[','').replace(']','').replace('{','').replace('}','')\
	    .replace('zip_codes:', '')
        cursor = get_db().cursor()
        cursor.execute(
                "SELECT  email\
		 FROM donor WHERE zipcode \
		 IN({zipcodes})".format(zipcodes=formatted_zipcode) 
            )
	results = cursor.fetchall()
	#change to list and not json 
	jsonresults = json.dumps(results)
#       got all the emails from the db
        email_body = form.body.data
        body = "<html><head></head><body><pre>{}</pre></body></html>".format(email_body)
         # based off of book's user pref's code
        #for loop here going through all emails in list
    
        body = Template(body)
        mail.send_mail(sender="sonalchatter91@gmail.com", \
                to="sonal.chatter@tufts.edu",\
                subject=form.subject.data,\
                body=form.body.data,\
                html=body)
        success_message = "message sent!"
        success = True
    elif success == False:
        success_message = "The email specified is not in our system. Please try again."
 #   except :
  #      success_message = "There was an error sending your email. Please try again at another time."
#                pass
#        self.response.headers['Content-Type'] = 'application/json'
 #       obj = {
  #          'success': success,
   #         'message': success_message
    #    }
      #  self.response.out.write(json.dumps(obj))
 
        return render_template('emailadmin.html', user=users.get_current_user(), \
				form=form)

    elif form.errors:
         report_errors(form.errors)
         return render_template('emailadmin.html', user=users.get_current_user(), \
				form=form)
    return render_template('emailadmin.html', user=users.get_current_user(), \
				form=form, mce_key=get_mce_key())


  # Flask reuqires a return for every function 
    return render_template('emailadmin.html', user=users.get_current_user(), \
				form=form)
      

@app.route('/dashboard')
@institution_required
def dashboard():
    cursor = get_db().cursor()
    cursor.execute(
        "SELECT O_neg, O_pos, A_neg, A_pos, B_neg, B_pos, AB_neg, AB_pos "
        "FROM {} WHERE id=%s".format(g.account_type),
        (g.account_id,)
    )
    return render_template(
        'dashboard.html',
        record=cursor.fetchone()
    )


@app.route('/eligibility', methods=["GET", "POST"])
@donor_required
def eligibility_questionaire():
    form = eligibility.Form()
    if form.validate_on_submit():
        status = "Eligible"
        if form.age_min.data == "no":
            flash("Check your local state guidelines, some states let you donate starting at 16. If you are 17, you may donate blood, but additional requirements apply; please check your state for guidelines", Alert.info)
            status = "Ineligible"
        if form.age_max.data == "no":
            flash("Check your local state guidelines, some states require a doctor's note declaring you are in good health", Alert.info)
            status = "Unknown" if status != "Ineligible" else "Ineligible"
        if form.weight_min.data == "no":
            flash("Unfortunately, you must weigh at least 110lbs to donate blood", Alert.info)
            status = "Ineligible"
        if form.medication.data == "yes":
            flash("Bring list of all your medications with you to the donation location", Alert.info)
            status = "Unknown" if status != "Ineligible" else "Ineligible"
        if form.travel.data == "yes":
            flash("Bring list of all your travels, including which countries you visited, and when", Alert.info)
            status = "Unknown" if status != "Ineligible" else "Ineligible"
        if form.infection.data == "yes":
            flash("Individuals with an infection may not donate blood", Alert.info)
            status = "Ineligible"
        if form.recent_donation.data == "yes":
            flash("Please wait until at least 56 days before donating blood again", Alert.info)
            status = "Ineligible"
        cursor = get_db().cursor()
        cursor.execute("UPDATE donor SET eligibility=%s WHERE id=%s", (status, g.account_id))
        return redirect(url_for('index'))
    report_errors(form.errors)
    return render_template('eligibility.html', form=form)
            

#### BEGIN EVENTS ####
@app.route('/events/create', methods=['GET', 'POST'])
def createevent():
    #todo - need to be able to extract from the session - not sticking right now
    form = create.Form(inst_id=str(g.account_id))
    if form.validate_on_submit():
        logging.info(form.start_date.data)
        # form takes data in utc, we're using eastern times
        # todo - enable timezone based on user preferences
        start_date = form.start_date.data + datetime.timedelta(hours=5)
        end_date = form.end_date.data + datetime.timedelta(hours=5)
        new_event = events.Event(
            inst_id = form.inst_id.data,
            location = form.location.data,
            description = form.description.data,
            num_parallel=1,
            apt_slot=15,
            published=False,
            start_date= start_date,
            end_date = end_date,
            scheduled_for_deletion = False
        )
        new_event.put()
        current_date = start_date
        while current_date < end_date:
            time_slot = events.TimeSlot(
                start_time = current_date,
                can_be_scheduled=True,
                event=new_event.key,
                parent=new_event.key,
                scheduled_for_deletion=False
            )
            time_slot.put()
            current_date = current_date + datetime.timedelta(minutes=15)
        return redirect(url_for('viewevent', eid=new_event.key.id()))
    else:
        if form.errors:
            report_errors(form.errors)
        return render_template("events/create.html", form=form, api_key=get_maps_key())

@app.route('/events/edit', methods=['GET'])
@login_required
def editevent():
    event_id = None
    event= None
    form=None
    event_id = request.args['eid']
    if event_id:
        if g.account_type == 'bank':
            event_long = long(event_id)
            possible_event = events.Event.get_by_id(event_long)
            event=possible_event
            if possible_event:
                if possible_event.end_date < get_current_time():
                    flash("This event is over. It cannot be edited.", Alert.danger)
                    return redirect(url_for("viewevent", eid=event_id))
                form = update.Form(inst_id="this_is_a_test", event_id=event_id, location=event.location, description=event.description)
        else:
            abort(401)
    else:
        report_errors(form.errors)
    return render_template("events/edit.html", form=form, event=event)

@app.route('/events/update', methods=['POST'])
def updateevent():
    form = update.Form()
    if request.values.has_key('event_id'):
        update.event_id = request.values['event_id']
    eid = None
    if form.validate_on_submit():
        event_long = long(form.data['event_id'])
        logging.info("event long")
        logging.info(event_long)
        possible_event = events.Event.get_by_id(event_long)
        if possible_event:
            event = possible_event
            event.location = form.location.data
            event.description = form.description.data
            event.put()
            flash("Event details updated successfully", Alert.success)
            return redirect(url_for('viewevent', eid=event.key.id()))
    else:
        report_errors(form.errors)
        if form.data.has_key('event_id'):
            eid = form.data['event_id']
    return redirect(url_for('viewevent', eid=eid))

@app.route('/events/delete', methods=['POST'])
def deleteevent():
    event_id = request.form['eid']
    if event_id:
        event_long = long(event_id)
        possible_event = events.Event.get_by_id(event_long)
        if possible_event:
            possible_event.scheduled_for_deletion = True
            possible_event.put()
            time_slots = events.TimeSlot.query(ancestor = possible_event.key)
            if time_slots:
                for slot in time_slots:
                    slot.scheduled_for_deletion = True
                ndb.put_multi(time_slots)
            flash("Event removed.", Alert.success)
    return redirect("")

@app.route('/events/publish', methods=['POST'])
def publishevent():
    eid = None
    if request.values.has_key('eid'):
        eid = request.values['eid']
        event = events.Event.get_by_id(long(eid))
        if event:
            event.published = True
            event.put()
            flash('Event is now available to the public!', Alert.success)
    return redirect(url_for('viewevent', eid=eid))

@app.route('/events/manage')
@login_required
@bank_required
def manageevent():
    offset = 0
    if(request.values.has_key('offset')):
        offset = int(request.values['offset'])
    fewer_events = offset >= 10
    upcoming_events = events.list_configured_events(id=str(g.account_id), limit=10, offset=offset)
    total_events = events.count_configured_events(id=str(g.account_id))
    more_events = offset + 10 < total_events
    event_list = []
    for event in upcoming_events:
        date = events.get_as_eastern(event.start_date)
        event_list.append({
            'location': event.location,
            'date': date.strftime("%B %d, %Y at %I:%M %p"),
            'start_date': event.start_date,
            'end_date': event.end_date,
            'is_public' : event.published,
            'key': event.key,
            'is_over':event.end_date < get_current_time()
        })
    return render_template('events/manage.html', event_list=event_list, current_time=get_current_time(), more_events=more_events, fewer_events=fewer_events, offset=offset)

@app.route("/events/view", methods=['POST', 'GET'])
def viewevent():
    current_apt=None
    apt_url=None
    start_date=None
    end_date=None
    current_time = datetime.datetime.now()
    if request.values.has_key('eid'):
        event_id = request.values['eid']
    else:
        event_id = None
    event = None
    url_params=None
    apt_url=None
    apt_time=None
    time_slots = None
    if event_id:
        event_long = long(event_id)
        possible_event = events.Event.get_by_id(event_long)
        event = possible_event
        embed_params = {'key': get_maps_key(), 'q': event.location}
        url_params = urllib.urlencode(embed_params)
        start_date=events.get_as_eastern(event.start_date)
        end_date=events.get_as_eastern(event.end_date)
        if event and users.get_current_user() and g.account_id:
            current_apt = events.TimeSlot.query(ancestor=event.key)\
                .filter(events.TimeSlot.user_id==str(g.account_id)).get()
            if current_apt:
                detail_url = request.base_url + '?eid='+event_id
                apt_date = (current_apt.start_time).strftime("%Y%m%dT%H%M00Z")\
                           +"/"+(current_apt.start_time+datetime.timedelta(minutes=30)).strftime("%Y%m%dT%H%M00Z")
                details = 'For details, see %s' % detail_url
                params = {
                    'text' : "Blood Donation Appointment",
                    'dates' : apt_date,
                    'details' : details,
                    'location' : event.location,
                }
                apt_url = urllib.urlencode(params)
                apt_time=events.get_as_eastern(current_apt.start_time)
            slots = events.list_open_slots(event)
            time_slots = []
            for slot in slots:
                date = events.get_as_eastern(slot.start_time)
                time_slots.append({
                    'id' : slot.key.id(),
                    'date' : date.strftime("%I:%M %p")
                })
    return render_template("events/view.html",
                           event=event,
                           time_slots=time_slots,
                           current_apt=current_apt,
                           url_params=url_params,
                           current_time=current_time,
                           apt_url=apt_url,
                           apt_time=apt_time,
                           start_date=start_date,
                           end_date=end_date)

@app.route("/events/schedule", methods=['POST'])
def scheduleapt():
    event_id = None
    logging.info(request.values.has_key('tsid'))
    logging.info(request.values.has_key('eid'))
    logging.info(users.get_current_user())
    if request.values.has_key('tsid') and request.values.has_key('eid') and g.account_id:
        user_id = str(g.account_id)
        event_id = request.values['eid']
        apt_id = request.values['tsid']
        time_slot = events.get_time_slot(apt_id, event_id)
        logging.info(time_slot)
        if time_slot and time_slot.can_be_scheduled and not time_slot.scheduled_for_deletion:
            if time_slot.user_id:
                if time_slot.user_id == user_id:
                    time_slot.user_id = None
                    time_slot.put()
                    flash("Appointment cancelled.", Alert.info)
                else:
                    flash("This timeslot has already been scheduled by another user. Try another time.", Alert.danger)
            else:
                time_slot.user_id = user_id
                time_slot.put()
                flash("Appointment scheduled!", Alert.success)
        else:
            flash("Unable to find specified timeslot", Alert.danger)
    return redirect(url_for("viewevent", eid=event_id))

@app.route("/events/notes", methods=['POST'])
def updateaptnote():
    event_id = None
    if request.values.has_key('tsid') and request.values.has_key('eid') and g.account_id \
            and request.values.has_key('note'):
        user_id = str(g.account_id)
        event_id = request.values['eid']
        apt_id = request.values['tsid']
        time_slot = events.get_time_slot(apt_id, event_id)
        if time_slot and time_slot.user_id == user_id:
            time_slot.notes = request.values['note']
            flash("Updated notes", Alert.success)
            time_slot.put()
    return redirect(url_for("viewevent", eid=event_id))

@app.route("/events/tasks/notify")
def notifiyevent():
    logging.info("running the event notification hander")
    events_to_notify = events.get_events_to_notify()
    sender_address= 'admin@%s.appspotmail.com' % get_id()
    for event in events_to_notify:
        time_slots = events.TimeSlot.query(ancestor=event.key)
        logging.info(event.location)
        slot_keys = []
        user_ids = []
        for slot in time_slots:
            slot_keys.append(slot.key)
            logging.info(slot.start_time)
            logging.info(slot.user_id)
            if slot.user_id:
                user_ids.append(slot.user_id)
                cursor = get_db().cursor()
                cursor.execute(
                    "SELECT email FROM donor WHERE id = {}".format(int(slot.user_id))
                )
                row = cursor.fetchone()
                if row:
                    logging.info("found a user's email")
                    logging.info(row[0])
                    email_address=row[0]
                    start_time = events.get_as_eastern(slot.start_time)
                    body="This is a notifcation that you have an upcoming blood donation appoinment on {}. " \
                         "Your appointment will take place at {}. Please make sure to arrive promptly."\
                        .format(start_time.strftime("%B %d, %Y at %I:%M %p"), event.location)
                    mail.send_mail(sender=sender_address,
                                   to=email_address,
                                   subject="Don't Forget Your Upcoming Donation Appointment!",
                                   body=body)

                else:
                    logging.info("could not find user associated with id {}", slot.user_id)
    return redirect("/"), 200


@app.route("/events/tasks/delete")
def deleteevents():
    logging.info("running the delete event handler")
    events_to_delete = events.Event.query().filter(events.Event.scheduled_for_deletion == True).fetch(10)
    sender_address= 'admin@%s.appspotmail.com' % get_id()
    for event in events_to_delete:
        time_slots = events.TimeSlot.query(ancestor=event.key)
        slot_keys = []
        for slot in time_slots:
            slot_keys.append(slot.key)
            if slot.user_id:
                cursor = get_db().cursor()
                cursor.execute(
                    "SELECT email FROM donor WHERE id = {}".format(int(slot.user_id))
                )
                row = cursor.fetchone()
                if row:
                    start_time = events.get_as_eastern(event.start_date)
                    email_address = row[0]
                    body = "This is a notification that the blood donation event at {} on {} has been cancelled. You are receiving this message beause you are on our records as having an appointment.".format(event.location, start_time.strftime("%B %d, %Y"))
                    mail.send_mail(sender=sender_address,
                                   to=email_address,
                                   subject="Blood Donation Event Cancelled",
                                   body=body)
        ndb.delete_multi(slot_keys)
    return redirect("/"), 200

@app.route("/events/download/aptlist.csv")
@login_required
@bank_required
def download():
    logging.info("running the csv writer")
    event_id = None
    event = None
    header = ["Time", "Patient ID", "Notes"]
    if request.values.has_key('eid'):
        event_id = request.values['eid']
        event = events.Event.get_by_id(int(event_id))
    def generate(event):
        yield ','.join(header)+'\n'
        if event:
            time_slots = events.TimeSlot.query(ancestor=event.key)
            for slot in time_slots:
                id_string = ""
                if slot.user_id:
                    id_string = str(slot.user_id)
                notes = ""
                if slot.notes:
                    notes = slot.notes
                start_time = events.get_as_eastern(slot.start_time).strftime("%B %d %Y at %I:%M %p")
                row = [
                    start_time,
                    id_string,
                    """%s""" % notes,
                ]
                yield ','.join(row) + '\n'
        else:
            yield ',,\n'
    return Response(generate(event), mimetype='text/csv')



#### END EVENTS ####


@app.route('/find_donors', methods=['GET', 'POST'])
def find_donors():
    """
    Find all donors within a desired radius based on zipcode input.
    """
    form = radius.Form()
    if form.validate_on_submit():
	url = "https://www.zipcodeapi.com/rest/{key}/radius.json/{zipcode}/{distance}/miles?minimal".format(key=get_zipcode_key(), \
	   zipcode='{:05d}'.format(form.zipcode.data),\
	   distance='{:03d}'.format(form.radius.data))
	
	response = requests.get(url)
  	decoded = json.loads(response.text)
  #      import pdb; pdb.set_trace()
	zipcode_string = str(decoded)
	formatted_zipcode = zipcode_string.replace("u'",'').replace("'",'')\
	    .replace('[','').replace(']','').replace('{','').replace('}','')\
	    .replace('zip_codes:', '')
  #	return formatted_zipcode
        cursor = get_db().cursor()
        cursor.execute(
                "SELECT id, email, phone, zipcode,contact, outreach \
		 FROM donor WHERE zipcode \
		 IN({zipcodes})".format(zipcodes=formatted_zipcode) 
            )
	results = cursor.fetchall()
	jsonresults = json.dumps(results)
        flash("We found some donors", Alert.success)
	return jsonresults
   #     return redirect(url_for('find_donors'))
    elif form.errors:
        report_errors(form.errors)
  #  form.radius.data = request.args.get("inst")
        return render_template(
            'find_donors.html', form=form)
    return render_template(
        'find_donors.html', form=form)
