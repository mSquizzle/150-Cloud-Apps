from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateField, IntegerField, validators

from util import InlineRadioWidget

class Form(FlaskForm):
    age_min = RadioField("Are you over 18?",
        validators=[validators.DataRequired("Age minimum field required")], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    age_max = RadioField("Are you under 76?",
        validators=[validators.DataRequired("Age maximum field required")], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    weight_min = RadioField("Do you weigh over 110lbs?",
        validators=[validators.DataRequired("Weight minimum field required")], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    medication = RadioField("Do you take any prescription medications?",
        validators=[validators.DataRequired("Medication field required")], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    travel = RadioField("Have you traveled outside of the US or Canada in the last 3 years?",
        validators=[validators.DataRequired("Travel field required")], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    infection = RadioField("Do you currently have an untreated infection?",
        validators=[validators.DataRequired("Infection field required")], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
    recent_donation = RadioField("Have you donated blood in the past 8 weeks?",
        validators=[validators.DataRequired("Recent donation field required")], choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], widget=InlineRadioWidget())
