from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, validators

from util import BootstrapRadioWidget

class Form(FlaskForm):
    institution = RadioField('Institution Type', validators=[
        validators.DataRequired('Institution type choice is required')
    ], choices=[
        ('hospital', 'Hospital'),
        ('bank', 'Blood Bank')
    ], widget=BootstrapRadioWidget())
    email = StringField('Email', validators=[
        validators.DataRequired('Email field is required'),
        validators.Email(message='Invalid email')
    ])
    password = PasswordField('Password', validators=[
        validators.DataRequired('Password field is required')
    ])
