from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateField, IntegerField, validators, HiddenField

class Form(FlaskForm):
    event_id = HiddenField("Event ID")
    inst_id = HiddenField("Institution ID")
    location = StringField('Location', validators=[
        validators.DataRequired('Location is required'),
    ])
    description = StringField('Description')