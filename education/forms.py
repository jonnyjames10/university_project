from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, MultipleFileField, FileField, RadioField, IntegerField, SelectMultipleField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, InputRequired, Optional, NumberRange
from education.models import User
from datetime import datetime, timedelta

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators = [DataRequired()])
    last_name = StringField('Last Name', validators = [DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email(message='Must be a valid email')])
    password = PasswordField('Password',validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters long')])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password', message='Passwords do not match')])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    submit = SubmitField('REGISTER')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email address is already associated with an account.')

    def validate_password(self, password):
        if password.data.islower() or password.data.isupper():
            raise ValidationError('Password must contain both upper and lower case letters.')
        elif any(char.isdigit() for char in password.data) == False:
            raise ValidationError('Password must contain at least one number.')
    
    def validate_date_of_birth(self, date_of_birth):
        if datetime.now() - date_of_birth.data < 0:
            raise ValidationError('Date of birth cannot be from after todays date.')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Login')

