from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateField, IntegerField, validators

from util import InlineRadioWidget

class Form(FlaskForm):
    age_min = RadioField("Are you over 18?",
        validators=[validators.DataRequired()], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    age_max = RadioField("Are you under 76?",
        validators=[validators.DataRequired()], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    weight_min = RadioField("Do you weigh over 110lbs?",
        validators=[validators.DataRequired()], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    medication = RadioField("Do you take any prescription medications?",
        validators=[validators.DataRequired()], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    travel = RadioField("Have you traveled outside of the US or Canada in the last 3 years?",
        validators=[validators.DataRequired()], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    infection = RadioField("Do you currently have an untreated infection?",
        validators=[validators.DataRequired()], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    recent_donation = RadioField("Have you donated blood in the past 8 weeks?",
        validators=[validators.DataRequired()], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
