from flask_wtf import FlaskForm
<<<<<<< HEAD
from wtforms import Form, StringField, PasswordField, validators, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

=======
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
>>>>>>> f5184448c81a1479e7114aec64b6b9bc69fdf47f

class LoginForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=4, max=25)], render_kw={"placeholder": "Username", "class": "form-control"})
    password = PasswordField('Password', [DataRequired(), Length(min=6, max=35)], render_kw={"placeholder": "Password", "class": "form-control"})
<<<<<<< HEAD

    login_button = SubmitField('Login', render_kw={"class": "btn btn-primary"})

class RegistrationForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', [DataRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', [DataRequired(), Length(min=6, max=35)])
    confirm_password = PasswordField('Confirm Password', [DataRequired(), EqualTo('password', message='Passwords must match')])

    register_button = SubmitField('Register')
=======
    login_button = SubmitField('Login', render_kw={"class": "btn-login"})

def get_title_list():
    return [("void", "--Select title--"), ("Ms.", "Ms."), ("Mr.", "Mr."), ("Mrs.", "Mrs."), ("Dr.", "Dr."), ("Prof.", "Prof."), ("Dra.", "Dra."), ("Atty.", "Atty.")]


def get_gender_list():
    return [("void", "--Select title--"), ("Male", "Male"), ("Female", "Female"), ("Other", "Other")]

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', [DataRequired(), Length(min=2, max=25)], render_kw={"placeholder": "Enter your first name", "class": "first-name"})
    last_name = StringField('Last Name', [DataRequired(), Length(min=2, max=25)], render_kw={"placeholder": "Enter your last name", "class": "last-name"})
    title = SelectField('Title', choices=get_title_list(), default="void", render_kw={"class": "form-control"})
    birth_date = DateField('Birth Date', format='%Y-%m-%d', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "YYYY-MM-DD"})
    gender = SelectField('Gender', choices=get_gender_list(), default="void", render_kw={"placeholder": "--Select Gender--", "class": "form-control"})
    phone_number = StringField(
        'Phone Number',
        [DataRequired(), Length(min=10, max=15), Regexp(r'^\+?[0-9]*$', message="Invalid phone number")],
        render_kw={"placeholder": "Enter your phone number", "class": "form-control"}
    )
    username = StringField('Username', [DataRequired(), Length(min=4, max=25)], render_kw={"placeholder": "Enter your username", "class": "form-control"})
    email = StringField('Email', [DataRequired(), Email(message='Invalid email'), Length(max=50)], render_kw={"placeholder": "Enter your email", "class": "form-control"})
    password = PasswordField('Password', [DataRequired(), Length(min=6, max=35)], render_kw={"placeholder": "Enter your password", "class": "form-control"})
    confirm_password = PasswordField('Confirm Password', [DataRequired(), EqualTo('password', message='Passwords must match')], render_kw={"class": "form-control", "placeholder": "Confirm your password"})

    # Address fields
    country = SelectField('Country', choices=[], validators=[DataRequired()], render_kw={"id": "country", "class": "form-control"})
    province = SelectField('Province', choices=[], default="void", validators=[DataRequired()], render_kw={"id": "province", "class": "form-control"})
    city = SelectField('City', choices=[], default="void", validators=[DataRequired()], render_kw={"id": "city", "class": "form-control"})
    barangay = SelectField('Barangay', choices=[], default="void", validators=[DataRequired()], render_kw={"id": "barangay", "class": "form-control"})
    postal_code = StringField('Postal Code', [DataRequired(), Length(min=4, max=10)], render_kw={"id": "postal_code", "class": "form-control", "readonly": True})
    register_button = SubmitField('Register', render_kw={"class": "btn-register"})
>>>>>>> f5184448c81a1479e7114aec64b6b9bc69fdf47f
