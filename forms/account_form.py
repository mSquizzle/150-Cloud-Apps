from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators

class Form(FlaskForm):
    institution = RadioField('Institution Type', validators=[
        validators.DataRequired("Institution type field required")
    ], choices=[
        ('hospital', 'Hospital'),
        ('bank', 'Blood Bank')
    ])
    email = StringField('Email', validators=[
        validators.DataRequired('Email field is required'),
        validators.Email(message='Invalid email')
    ])
    name = StringField('Institution Name', validators=[
        validators.DataRequired('Institution field is required'),
    ])
    password = PasswordField('Password', validators=[
        validators.DataRequired('Password field is required')
    ])
    repeat_password = PasswordField('Repeat Password', validators=[
        validators.DataRequired('Repeat password field is required')
    ])

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.password.data != self.repeat_password.data:
            field.repeat_password.errors.append("Passwords must match")
            return False
        return True
