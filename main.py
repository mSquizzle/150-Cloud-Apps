from flask import Flask, render_template, request

app = Flask (__name__)

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

@app.route('/account/secure-account')
def secure_account():
    return render_template('accounts/secure-account.html')
