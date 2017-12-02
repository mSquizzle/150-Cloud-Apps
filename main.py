from flask import Flask, render_template, request, url_for, flash, \
        session, g, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from google.appengine.api import users

from forms import login_form, account_form
import os, re

app = Flask (__name__)

# necessary for keeping client-side sessions secure
app.secret_key = os.urandom(24)

# check if app is running in production
production = os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')

if not production:
    app.debug = True


class Alert:
    """
    Bootstrap classes used for flashing messages to the client. Sets
    the category of the message which is processed by a base template.
    """
    success = "alert-success"
    info = "alert-info"
    warning = "alert-warning"
    danger = "alert-danger"


# TODO: make db connection here
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
    # check for authenticated individual
    user = users.get_current_user()
    if user:
        g.authenticated = True
        g.account = "Individual"
        g.user = user
        g.logout = users.create_logout_url(url_for('index'))
    # check for authenticated institution
    elif 'institution' in session:
        g.authenticated = True
        g.account = "Institution"
        g.user = session['institution']
        g.logout = url_for('logout')
    else:
        g.authenticated = False
        g.individual_login = users.create_login_url(redirect_url())
        g.institution_login = url_for('login')
    
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if g.get('db'):
        g.db.close()

def get_account(path=None):
    # overwrite if not specified
    path = request.path
    user = users.get_current_user()
    account = {}
    if not user:
        account.update(
            user = None,
            login = users.create_login_url(path),
        )
    else:
        account.update(
            user = user,
            kind = 'individual',
            logout = users.create_logout_url(path),
        )
    return account

def redirect_url(default='index'):
    """
    Helper function which chooses a url to redirect the client to.
    """
    return request.args.get('next') or \
        request.referrer or \
        url_for(default)

def report_errors(err):
    for field_name, field_errors in err.iteritems():
        flash("{} field error: {}".format(field_name, field_errors[0]), Alert.warning)

################################################################################
#                                  Routing                                     #
################################################################################

@app.route('/')
def index():
    return render_template(
        'index.html',
        account=get_account()
    )

@app.route('/faq')
def faq():
    return render_template(
        'faq.html',
        account=get_account()
    )

@app.route('/about')
def about():
    return render_template(
        'about.html',
        account=get_account()
    )

@app.route('/account/choose-account')
def choose_account():
    return render_template(
        'accounts/choose-account.html',
        account=get_account()
    )

@app.route('/account/create-account', methods=['GET', 'POST'])
def create_account():
    form = account_form.Form()
    if request.method == 'POST':
        if form.validate_on_submit():
            # TODO: create institutional account
            flash("Successfully created acount", Alert.success)
            return redirect(url_for('index'))
        else:
            report_errors(form.errors)
            return redirect(redirect_url())
    else:
        # handle get request
        return render_template(
            'accounts/create-account.html',
            account=get_account(),
            form=account_form.Form()
        )

@app.route('/account/login', methods=['GET', 'POST'])
def login():
    form = login_form.Form()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed = "bogus" # TODO: g.db.execute(select... where =form.email.data)
            if not hashed:
                flash('Unable to find account', Alert.warning)
                return redirect(redirect_url())
            elif check_password_hash(hashed, form.password.data):
                session['institution'] = username
                return redirect(url_for('index'))
            else:
                flash('Incorrect password', Alert.warning)
                return redirect(redirect_url())
        else:
            report_errors(form.errors)
            return redirect(redirect_url())
    else:
        return render_template(
            'accounts/login.html',
            account=get_account(),
            form=form
        )

@app.route('/account/logout')
def logout():
    # invalidate institution username from the session and redirect to homepage
    session.pop('institution', None)
    return redirect(url_for('index'))

@app.route('/settings')
def settings():
    return render_template(
        'settings.html',
        account=get_account())

@app.route("/emailadmin")
def emailadmin():
    return render_template(
        'emailadmin.html',
        account=get_account())
