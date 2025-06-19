from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', [DataRequired(), Length(min=6, max=35)], render_kw={"placeholder": "Password", "class": "form-control", "autocomplete": "off"})

    login_button = SubmitField('Login', render_kw={"class": "btn btn-primary"})

class RegistrationForm(FlaskForm):
    # Personal Information
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={"placeholder": "Enter your first name"})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={"placeholder": "Enter your last name"})
    title = SelectField('Title', choices=[('', '--Select Title--'), ('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.')], default='', validators=[Optional()])
    birth_date = DateField('Birth Date', validators=[DataRequired()], render_kw={"type": "date", "autocomplete": "off"})
    gender = SelectField('Gender', choices=[('', '--Select Gender--'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='', validators=[Optional()])
    phone_number = StringField('Phone Number', validators=[DataRequired()], render_kw={"placeholder": "Enter your phone number"})
    
    # Account Information
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Enter username", "autocomplete": "off"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "Enter password", "autocomplete": "off"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Confirm password"})
    
    # Address Information
    country = SelectField('Country', choices=[('void', '--Select country--')], default='void')
    province = SelectField('Province', choices=[('void', '--Select province--')], default='void')
    city = SelectField('City', choices=[('void', '--Select city--')], default='void')
    barangay = SelectField('Barangay', choices=[('void', '--Select barangay--')], default='void')
    postal_code = StringField('Postal Code', render_kw={"placeholder": "Postal code will be filled automatically", "readonly": True})
    
    # Submit Button
    register_button = SubmitField('Register', render_kw={"class": "btn-register"})


class AdminLoginForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=4, max=25)], render_kw={"placeholder": "Username", "class": "form-control"})
    password = PasswordField('Password', [DataRequired(), Length(min=6, max=35)], render_kw={"placeholder": "Password", "class": "form-control"})

    login_button = SubmitField('Login', render_kw={"class": "btn btn-primary"})
