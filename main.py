from flask import Flask, render_template, request, url_for, flash, \
        session, g, redirect, abort
from werkzeug.security import generate_password_hash, check_password_hash
from google.appengine.api import users
import pymysql

from forms import login_form, account_form, donor
import os, re
from functools import wraps, partial

app = Flask (__name__)
app.config.from_pyfile('./config.py')


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
        g.connection = pymysql.connect(**app.config['DB_CONNECTION'])
    return g.connection


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
        g.institution_login = url_for('login')

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
        row = None
        with get_db().cursor() as cursor:
            cursor.execute(
                "SELECT id FROM donor WHERE email = %s",
                (user.email(),)
            )
            row = cursor.fetchone()
        if row:
            g.authenticated = True
            g.account_type = 'donor'
            g.account_id = row['id']
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

################################################################################
#                                  Routing                                     #
################################################################################

@app.route('/')
def index():
    return render_template('index.html')


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
    form = account_form.Form()
    if form.validate_on_submit():
        with get_db().cursor() as cursor:
            cursor.execute(
                "INSERT INTO {} (hashed, name, phone, email, zipcode)"
                "VALUES (%s, %s, %s, %s, %s)".format(form.institution.data),
                (generate_password_hash(form.password.data),
                form.name.data, "phone", form.email.data, 1111)
            )
        flash("Successfully created acount", Alert.success)
        return redirect(url_for('login'))
    elif form.errors:
        report_errors(form.errors)
    elif request.args.get("inst"):
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
        with get_db().cursor() as cursor:
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
def login():
    form = login_form.Form()
    if form.validate_on_submit():
        row = None
        with get_db().cursor() as cursor:
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
        elif check_password_hash(row['hashed'], form.password.data):
            session['authenticated'] = True
            session['account_type'] = form.institution.data
            session['account_id'] = row['id']
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


@app.route("/emailadmin")
def emailadmin():
    return render_template('emailadmin.html')
