from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateTimeField, IntegerField, validators, HiddenField
import datetime

class Form(FlaskForm):
    inst_id = HiddenField("Institution ID")
    location = StringField('Location', validators=[
        validators.DataRequired('Location is required'),
    ])
    description = StringField('Description')
    start_date = DateTimeField('Start Date',
                               default=datetime.datetime.now(),
                                validators=[validators.DataRequired('Start Date is required')],format='%Y-%m-%d %H:%M')
    end_date = DateTimeField('End Date',
                             default=datetime.datetime.now()+datetime.timedelta(hours=1),
                              validators=[validators.DataRequired('End Date is required')], format='%Y-%m-%d %H:%M')

    def validate(self):
        status = False
        if FlaskForm.validate(self):
            if self.start_date >= self.end_date:
                self.end_date.errors.append("End Date cannot before Start Date")
            else:
                status = True
        return status