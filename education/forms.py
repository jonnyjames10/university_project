from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, HiddenField, DateField, SelectMultipleField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, InputRequired, Optional, NumberRange
from education.models import User
from datetime import datetime, timedelta, date

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators = [DataRequired()])
    last_name = StringField('Last Name', validators = [DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email(message='Must be a valid email')])
    password = PasswordField('Password',validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters long')])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password', message='Passwords do not match')])
    school = StringField('School Name', validators=[DataRequired()])
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
        if date.today() <= date_of_birth.data:
            raise ValidationError('Date of birth must be before todays date.')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Login')

class PointsForm(FlaskForm):
    dbPoints = HiddenField('dbPoints', validators = [DataRequired()])
    marks = HiddenField('Marks', validators=[DataRequired()])
    activity_id = HiddenField('activityID', validators=[DataRequired()])
    submit = SubmitField('Finish')

class NewClassForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    students = SelectMultipleField('Students', choices=[], validators=[DataRequired()], coerce=int)
    submit = SubmitField('Create')

class SetHomeworkForm(FlaskForm):
    activities = SelectField('Activity', choices=[], validators=[DataRequired()], coerce=int)
    title = StringField('Title', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Set Homework')

    def validate_due_date(self, due_date):
        if date.today() >= due_date.data:
            raise ValidationError('Due date must be after todays date.')

class QuestionForm(FlaskForm):
    q1 = RadioField('', choices=[], validators=[DataRequired()])
    q2 = RadioField('', choices=[], validators=[DataRequired()])
    q3 = RadioField('', choices=[], validators=[DataRequired()])
    q4 = RadioField('', choices=[], validators=[DataRequired()])
    q5 = RadioField('', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')