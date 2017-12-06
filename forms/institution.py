#!/usr/bin/env python

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators

from util import BootstrapRadioWidget

class Form(FlaskForm):
    institution = RadioField('Institution Type', validators=[
        validators.DataRequired("Institution type field required")
        ], choices=[
        ('hospital', 'Hospital'),
        ('bank', 'Blood Bank')
        ], widget=BootstrapRadioWidget()
    )
    email = StringField('Email', validators=[
        validators.DataRequired('Email field is required'),
        validators.Email(message='Invalid email')
        ]
    )
    name = StringField('Institution Name', validators=[
        validators.DataRequired('Institution field is required'),
        ]
    )
    password = PasswordField('Password', validators=[
        validators.DataRequired('Password field is required')
        ]
    )
    repeat_password = PasswordField('Repeat Password', validators=[
        validators.DataRequired('Repeat password field is required')
        ]
    )

    def validate(self):
        status = True
        if not FlaskForm.validate(self):
            status = False
        if self.password.data != self.repeat_password.data:
            self.repeat_password.errors.append("Passwords must match")
            status = False
        return status
