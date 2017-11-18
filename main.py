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

@app.route('/')
def index():
    flash('This is a test', Alert.info)
    return render_template('index.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/account/choose-account')
def choose_account():
    return_url = url_for("index")
    env = {"login_url": users.create_login_url(return_url)}
    return render_template('accounts/choose-account.html', **env)

@app.route('/account/secure-account')
def secure_account():
    return render_template('accounts/secure-account.html')

@app.route('/account/create-account')
def create_account():
    return render_template('accounts/create-account.html')
