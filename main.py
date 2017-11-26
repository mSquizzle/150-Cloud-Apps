from flask import Flask, render_template, request, url_for, flash
import os
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

def get_base_env():
    user = users.get_current_user()
    logout_url = users.create_logout_url("/")
    env = {"user": user, "logout_url": logout_url}
    return env


@app.route('/')
def index():
    flash('This is a test', Alert.info)
    #user = users.get_current_user()
    #logout_url = users.create_logout_url("/")
    env = get_base_env()
    return render_template('index.html', **env)

@app.route('/faq')
def faq():
    env = get_base_env()
    return render_template('faq.html', **env)

@app.route('/about')
def about():
    env = get_base_env()
    return render_template('about.html', **env)

@app.route('/account/choose-account')
def choose_account():
    env = get_base_env()
    return_url = url_for("index")
    env["login_url"] = users.create_login_url(return_url)
    return render_template('accounts/choose-account.html', **env)

@app.route('/account/secure-account')
def secure_account():
    env = get_base_env()
    return render_template('accounts/secure-account.html', **env)

@app.route('/account/create-account')
def create_account():
    env = get_base_env()
    return render_template('accounts/create-account.html', **env)

@app.route('/settings')
def settings():
    env = get_base_env()
    return render_template('settings.html', **env)

@app.route("/emailadmin")
def emailadmin():
    env = get_base_env()
    return render_template('emailadmin.html', **env)