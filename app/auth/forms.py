from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp
)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        Length(min=3, max=64, message='Username must be 3–64 characters.'),
        Regexp(r'^[A-Za-z0-9_.\-]+$',
               message='Only letters, numbers, dots, underscores, and hyphens.')
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Enter a valid email address.'),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    remember_me = BooleanField('Keep me signed in')
    submit = SubmitField('Sign In')


class TwoFactorForm(FlaskForm):
    token = StringField('6-Digit Code', validators=[
        DataRequired(message='Authentication code is required.'),
        Length(min=6, max=6, message='Code must be exactly 6 digits.'),
        Regexp(r'^\d{6}$', message='Code must be 6 digits.')
    ])
    submit = SubmitField('Verify')


class Setup2FAForm(FlaskForm):
    token = StringField('Verification Code', validators=[
        DataRequired(message='Verification code is required.'),
        Length(min=6, max=6, message='Code must be exactly 6 digits.'),
        Regexp(r'^\d{6}$', message='Code must be 6 digits.')
    ])
    submit = SubmitField('Enable 2FA')
