from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateField, IntegerField, validators

from util import InlineRadioWidget

class Form(FlaskForm):
    outreach = RadioField("Can blood banks reach out to you?",
        validators=[validators.DataRequired()], choices=[
        ('YES', 'Yes'),
        ('NO', 'No')
    ], widget=InlineRadioWidget())
    contact = RadioField("What is your preferred method of communication?",
        validators=[validators.DataRequired()], choices=[
        ('Email', 'Email'),
        ('Phone', 'Phone')
    ], widget=InlineRadioWidget())
