from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators

class Form(FlaskForm):
    institution = RadioField('Institution Type', validators=[
        validators.DataRequired()
    ], choices=[
        ('hospital', 'Hospital'),
        ('blood_bank', 'Blood Bank')
    ])
    email = StringField('Email', validators=[
        validators.DataRequired('Email field is required'),
        validators.Email(message='Invalid email')
    ])
    name = StringField('Institution Name', validators=[
        validators.DataRequired('Institution field is required'),
    ])
    password = PasswordField('Password', validators=[
        validators.DataRequired('Password field is required')
    ])
    repeat_password = PasswordField('Repeat Password', validators=[
        validators.DataRequired('Repeat password field is required')
    ])
