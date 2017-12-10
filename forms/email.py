from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateField, IntegerField, validators

class Form(FlaskForm):
    zipcode = IntegerField('Zipcode', validators=[
        validators.DataRequired('Zip code field is required'),
        validators.NumberRange(0, 99999, 'Zip code must be within valid range'),
    ])
    radius = IntegerField('Radius(mi)', validators=[
        validators.DataRequired('Radius field is required'),
        validators.NumberRange(1, 200, 'Radius must be within valid range of 1 - 200'),
    ])
    subject = StringField('Subject', validators=[                           
        validators.DataRequired('Subject field is required'),                 
    ])                                                              
