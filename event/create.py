from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateTimeField, IntegerField, validators, HiddenField
import datetime
import logging
import pytz
from forms import util

class Form(FlaskForm):
    inst_id = HiddenField("Institution ID")
    location = StringField('Location', validators=[
        validators.DataRequired('Location is required'),
    ])
    description = StringField('Description')
    start_date = DateTimeField('Start Date',
                               default=datetime.datetime.now(tz=pytz.timezone("US/Eastern"))+datetime.timedelta(days=1),
                                validators=[validators.DataRequired('Start Date is required')],format='%Y-%m-%dT%H:%M')
    end_date = DateTimeField('End Date',
                             default=datetime.datetime.now(tz=pytz.timezone("US/Eastern"))+datetime.timedelta(days=1,hours=1),
                              validators=[validators.DataRequired('End Date is required')], format='%Y-%m-%dT%H:%M')
    apt_length = RadioField("Apointment Start Time",
                        default='15',
                         validators=[validators.DataRequired()], choices=[
            ('15', 'Every 15 Minutes'),
            ('30', 'Every 30 Minutes'),
            ('45', 'Every 45 Minutes'),
            ('60', 'Every 60 Minutes')
        ], widget=util.InlineRadioWidget())

    def validate(self):
        status = False
        if FlaskForm.validate(self):
            start_date = self.start_date.data
            end_date = self.start_date.data
            if start_date > end_date:
                self.end_date.errors.append("End Date cannot before Start Date")
            else:
                status = True
        return status