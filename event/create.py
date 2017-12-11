from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateTimeField, IntegerField, validators, HiddenField
import datetime
import logging
import pytz

class Form(FlaskForm):
    inst_id = HiddenField("Institution ID")
    location = StringField('Location', validators=[
        validators.DataRequired('Location is required'),
    ])
    description = StringField('Description')
    start_date = DateTimeField('Start Date',
                               default=datetime.datetime.now(tz=pytz.timezone("US/Eastern")),
                                validators=[validators.DataRequired('Start Date is required')],format='%Y-%m-%dT%H:%M')
    end_date = DateTimeField('End Date',
                             default=datetime.datetime.now(tz=pytz.timezone("US/Eastern"))+datetime.timedelta(hours=1),
                              validators=[validators.DataRequired('End Date is required')], format='%Y-%m-%dT%H:%M')

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