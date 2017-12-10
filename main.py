import os, re, datetime, urllib, requests, logging
from functools import wraps, partial

import requests
from requests_toolbelt.adapters import appengine
from google.appengine.api import users
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, url_for, flash, \
        session, g, redirect, abort
import datetime
import urllib
from event import events, create, update

from forms import login, institution, donor, radius, eligibility
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
    #todo - turn into environment variable
    return 'AIzaSyAfvS-E0xWdXEUvCryyyryLZAYNHAlGt5Y'


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

def _required(func, arg):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not g.get("authenticated") or g.get("account_type") != arg:
            abort(401)
        return func(*args, **kwargs)
    return decorated_view

donor_required = partial(_required, arg="donor")

bank_required = partial(_required, arg="bank")

hospital_required = partial(_required, arg="hospital")

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
    event_list = events.list_events()
    return render_template('index.html', event_list=event_list, current_time=datetime.datetime.now())


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
            (form.first_name.data, form.last_name.data, form.phone.data, form.zipcode.data, user.email())
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
    elif form.errors:
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


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/emailadmin')
def emailadmin():
    return render_template('emailadmin.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if g.account_type == 'donor':
        return ''
    else:
        cursor = get_db().cursor()
        cursor.execute(
            "SELECT * FROM {} WHERE id=%s".format(g.account_type),
            (g.account_id,)
        )
        return render_template(
            'dashboard.html',
            record=cursor.fetchone()
        )
@app.route('/eligibility')
@donor_required
def eligibility_questionaire():
    form = eligibility.Form()
    return render_template('eligibility.html', form=form)

            

#### BEGIN EVENTS ####
@app.route('/events/create', methods=['GET', 'POST'])
def createevent():
    #todo - need to be able to extract from the session - not sticking right now
    form = create.Form(inst_id="this_is_a_test")
    if form.validate_on_submit():
        new_event = events.Event(
            inst_id = form.inst_id.data,
            location = form.location.data,
            description = form.description.data,
            num_parallel=1,
            apt_slot=15,
            published=False,
            start_date=form.start_date.data,
            end_date = form.end_date.data,
            scheduled_for_deletion = False
        )
        new_event.put()
        current_date = new_event.start_date
        while current_date < form.end_date.data:
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
        return render_template("events/create.html", form=form)

@app.route('/events/edit', methods=['GET'])
def editevent():
    event_id = None
    event= None
    form=None
    event_id = request.args['eid']
    if event_id:
        event_long = long(event_id)
        possible_event = events.Event.get_by_id(event_long)
        event=possible_event
        form = update.Form(inst_id="this_is_a_test", event_id=event_id, location=event.location, description=event.description)
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

@app.route("/events/view", methods=['POST', 'GET'])
def viewevent():
    current_apt=None
    current_time = datetime.datetime.now()
    if request.values.has_key('eid'):
        event_id = request.values['eid']
    else:
        event_id = None
    event = None
    url_params=None
    time_slots = None
    if event_id:
        event_long = long(event_id)
        possible_event = events.Event.get_by_id(event_long)
        event = possible_event
        embed_params = {'key': get_maps_key(), 'q': event.location}
        url_params = urllib.urlencode(embed_params)
        if event and users.get_current_user():
            current_apt = events.TimeSlot.query(ancestor=event.key).filter(events.TimeSlot.user_id==users.get_current_user().user_id()).get()
            time_slots = events.list_open_slots(event)
    return render_template("events/view.html", event=event, time_slots=time_slots, current_apt=current_apt, url_params=url_params, current_time=current_time)

@app.route("/events/schedule", methods=['POST'])
def scheduleapt():
    event_id = None
    logging.info(request.values.has_key('tsid'))
    logging.info(request.values.has_key('eid'))
    logging.info(users.get_current_user())
    if request.values.has_key('tsid') and request.values.has_key('eid') and users.get_current_user():
        user_id = users.get_current_user().user_id()
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


#### END EVENTS ####


@app.route('/find_donors', methods=['GET', 'POST'])
def find_donors():
    """
    Find all donors within a desired radius based on zipcode input.
    """
    form = radius.Form()
    if form.validate_on_submit():
	parameters = {"api_key": 'ZIPCODE_API_KEY',"format": "radius.json", \
	     "zipcode": form.zipcode.data, "distance": form.radius.data, \
	      "units": "miles?minimal" }
	response = requests.get("https://www.zipcodeapi.com/rest", params=parameters)
  #      if query comes back empty, then say there are no donors 
  #      with get_db().cursor() as cursor:
  #          cursor.execute(
  #              "SELECT zipcode FROM donor WHERE zipcode IN(all the zipcodes returned from api call) 
  #          )
        flash("We found some donors", Alert.success)
        return redirect(url_for('find_donors'))
    elif form.errors:
        report_errors(form.errors)
  #  form.radius.data = request.args.get("inst")
    return render_template(
        'find_donors.html', form=form)
