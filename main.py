from flask import Flask, render_template, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

import os, logging, re
from google.appengine.api import users

app = Flask (__name__)

# necessary for keeping client-side sessions secure
app.secret_key = os.urandom(24)

# check if app is running in production
production = os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')

if not production:
    app.debug = True

class Alert:
    success = "alert-success"
    info = "alert-info"
    warning = "alert-warning"
    danger = "alert-danger"

def get_account(path=None):
    # overwrite if not specified
    path = path or request.path
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

@app.route('/account/secure-account')
def secure_account():
    return render_template(
        'accounts/secure-account.html',
        account=get_account()
    )

@app.route('/account/create-account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        form = request.form
        # quick validation
        if form['pass'] != form['repeat_pass']:
            flash('Passwords do not match', Alert.warning)
        if not re.match(r'[^@]+@[^@]+\.[^@]+', form['email']):
            flash('Invalid email format', Alert.warning)
        return render_template(
            'accounts/create-account.html',
            account=get_account()
        )
    else:
        # handle get request
        return render_template(
            'accounts/create-account.html',
            account=get_account()
        )

@app.route('/bank/<int:bank_id>')
def bank_profile(bank_id):
    # TODO: get bank from DB
    return render_template(
        'bank.html',
        account=get_account(),
        bank=bank,
    )

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
