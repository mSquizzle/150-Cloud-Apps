from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateField, IntegerField, validators

class Form(FlaskForm):
    radius = IntegerField('Radius', validators=[
        validators.DataRequired('Radius field is required'),
        validators.NumberRange(1, 200, 'Radius must be within valid range'),
    ])
    zipcode = IntegerField('Zip Code', validators=[
        validators.DataRequired('Zip code field is required'),
        validators.NumberRange(0, 99999, 'Zip code must be within valid range'),
    ])
