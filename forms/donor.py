from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateField, IntegerField, validators

class Form(FlaskForm):
    first_name = StringField('First Name', validators=[
        validators.DataRequired('First name field is required'),
    ])
    last_name = StringField('Last Name', validators=[
        validators.DataRequired('Last name field is required'),
    ])
    phone = StringField('Phone Number', validators=[
        validators.DataRequired('Phone number field is required'),
    ])
    zipcode = IntegerField('Zip Code', validators=[
        validators.DataRequired('Zip code field is required'),
        validators.NumberRange(0, 99999, 'Zip code must be within valid range'),
    ])
    last_donation = DateField('Last donation')
    outreach = RadioField("Can blood banks reach out to you?",
        validators=[validators.DataRequired()], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ])
    contact = RadioField("What is your preferred method of communication?",
        validators=[validators.DataRequired()], choices=[
        ('email', 'Email'),
        ('phone', 'Phone')
    ])
