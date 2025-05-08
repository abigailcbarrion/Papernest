from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, validators, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=4, max=25)], render_kw={"placeholder": "Username", "class": "form-control"})
    password = PasswordField('Password', [DataRequired(), Length(min=6, max=35)], render_kw={"placeholder": "Password", "class": "form-control"})

    login_button = SubmitField('Login', render_kw={"class": "btn btn-primary"})

class RegistrationForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', [DataRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', [DataRequired(), Length(min=6, max=35)])
    confirm_password = PasswordField('Confirm Password', [DataRequired(), EqualTo('password', message='Passwords must match')])

    register_button = SubmitField('Register')