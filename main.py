from flask import Flask, render_template, request, url_for, flash, \
        session, g, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from google.appengine.api import users
import pymysql

from forms import login_form, account_form, donor
import os, re

app = Flask (__name__)
app.config.from_pyfile('./config.py')


class Alert:
    """
    Bootstrap classes used for flashing messages to the client. Sets
    the category of the message which is processed by a base template.
    """
    success = "alert-success"
    info = "alert-info"
    warning = "alert-warning"
    danger = "alert-danger"


def get_db():
    """Lazy-load function that makes a connection to the database. It is the
    clients responsibility to commit any changes. The connection is
    automatically closed at the end of the request by the close_db function.
    """
    if not hasattr(g, 'connection'):
        g.connection = pymysql.connect(**app.config['DB_CONNECTION'])
    return g.connection

# TODO: handle possibility of being logged in as both user types
@app.before_request
def authenticate():
    """
    Checks if the user is authenticated. Abstracts over the differences
    between individual and institutional users and stores important variables
    in the application context ("g") which is accessible from within the
    template rendering context. In the future, the database connection will
    also be performed in this subroutine.
    """
    def unauthenticated():
        g.authenticated = False
        g.individual_login = users.create_login_url(redirect_url())
        g.institution_login = url_for('login')

    user = users.get_current_user()
    # check if session already been authenticated
    if session.get("authenticated"):
        g.authenticated = True
        g.account_type = session.get("account_type")
        g.account_id = session.get("account_id")
        if g.account_type == "donor":
            g.logout = users.create_logout_url(url_for('index'))
        else:
            g.logout = url_for('logout')
    # just posted account details
    elif hasattr(request.url_rule, "rule") and url_for('complete_individual') in request.url_rule.rule:
        unauthenticated()
        return
    # check for donor account
    elif user:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT donor_id FROM donor WHERE email = %s",
                (user.email(),)
            )
        donor_id = cursor.fetchone()
        if donor_id:
            g.authenticated = True
            g.account_type = "donor"
            g.account_id = donor_id
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
    """Closes the database at the end of the request."""
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
    for field_name, field_errors in err.iteritems():
        flash(field_errors[0], Alert.warning)

################################################################################
#                                  Routing                                     #
################################################################################

@app.route('/')
def index():
    connection = pymysql.connect(**app.config['DB_CONNECTION'])
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
    Create a blood bank or hospital admin account
    """
    form = account_form.Form()
    if request.method == 'POST':
        if form.validate_on_submit():
            # TODO: create institutional account here
            conn = get_db()
            with conn.cursor() as cursor:
                pass
                # cursor.execute("INSERT INTO %s (short_name, full_name, phone_number) VALUES ()", ())
            flash("Successfully created acount", Alert.success)
            return redirect(url_for('index'))
        else:
            report_errors(form.errors)
    return render_template(
        'accounts/create-account.html',
        form=account_form.Form()
    )

@app.route('/account/complete-individual', methods=['POST'])
def complete_individual():
    form = donor.Form()
    if form.validate_on_submit():
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO donor (first_name, last_name, phone_number, email) VALUES (%s, %s, %s, %s)",
                (form.first_name.data, form.last_name.data, form.phone.data, "@example.com")
            )
        conn.commit()
        flash("Successfully created acount", Alert.success)
        return redirect(url_for('index'))
    report_errors(form.errors)
    return render_template(
        'accounts/complete_account.html',
        form=form
    )


@app.route('/account/login', methods=['GET', 'POST'])
def login():
    form = login_form.Form()
    if request.method == 'POST':
        if form.validate_on_submit():
            conn = get_db()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT hospital_id FROM %s WHERE email=%s;",
                    (form.institution.data, form.email.data)
                )
                hashed = cursor.fetchone()
                if not hashed:
                    flash('Unable to find account', Alert.warning)
                elif check_password_hash(hashed, form.password.data):
                    # TODO: also need to encode bank/hospital
                    session['name'] = donor_id
                    session['institution'] = "word"
                    return redirect(redirect_url())
                else:
                    flash('Incorrect password', Alert.warning)
        else:
            report_errors(form.errors)
    return render_template(
        'accounts/login.html',
        form=form
    )

@app.route('/account/logout')
def logout():
    # invalidate institution username from the session and redirect to homepage
    session.pop('institution', None)
    return redirect(url_for('index'))

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route("/emailadmin")
def emailadmin():
    return render_template('emailadmin.html')
