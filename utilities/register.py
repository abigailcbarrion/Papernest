from forms import RegistrationForm
from api import get_user_country, fetch_provinces, fetch_cities, fetch_barangays, fetch_postal_code
from flask import render_template, request, redirect, url_for, jsonify
from database_connection.connector import get_users_db

def save_user_to_db(user_data):
    """Save new user to SQLite database"""
    try:
        with get_users_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (
                    username, password, first_name, last_name, title,
                    birth_date, gender, phone_number, email, country,
                    province, city, barangay, postal_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(user_data.values()))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False

def check_username_exists(username):
    """Check if username already exists"""
    try:
        with get_users_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking username: {e}")
        return False

def setup_form_choices(form):
    """Setup dropdown choices"""
    country = get_user_country()
    form.country.choices = [("void", "--Select country--"), ("PH", country)]
    form.country.default = "void"
    form.process()
    
    provinces = fetch_provinces()
    form.province.choices = [("void", "--Select the province--")] + sorted(
        [(p['code'], p['name']) for p in provinces], key=lambda x: x[1].lower())
    form.city.choices = [("void", "--Select the city--")]
    form.barangay.choices = [("void", "--Select the barangay--")]

def get_postal_code_for_city(province_code, city_code):
    """Get postal code for selected city"""
    if not city_code:
        return None
    cities = fetch_cities(province_code)
    for city in cities:
        if city[0] == city_code:
            return city[2]
    return None

def create_user_data(form):
    """Create user data dictionary from form"""
    return {
        "username": form.username.data,
        "password": form.password.data,
        "first_name": form.first_name.data,
        "last_name": form.last_name.data,
        "title": form.title.data,
        "birth_date": form.birth_date.data,
        "gender": form.gender.data,
        "phone_number": form.phone_number.data,
        "email": form.email.data,
        "country": form.country.data,
        "province": form.province.data,
        "city": form.city.data,
        "barangay": form.barangay.data,
        "postal_code": form.postal_code.data
    }

def handle_register():
    """Handle user registration"""
    form = RegistrationForm(request.form)
    setup_form_choices(form)

    if request.method == 'POST' and form.validate():
        postal_code = get_postal_code_for_city(form.province.data, form.city.data)
        if postal_code:
            form.postal_code.data = postal_code

        if check_username_exists(form.username.data):
            return "Username already exists. Try another one."

        user_data = create_user_data(form)
        if save_user_to_db(user_data):
            return redirect(url_for('login'))
        else:
            return "Registration failed. Please try again."

    return render_template('register.html', registration_form=form)

def get_cities_json(province_code):
    """API endpoint for cities"""
    return {"cities": fetch_cities(province_code)}

def get_barangays_json(city_code):
    """API endpoint for barangays"""
    return {"barangays": fetch_barangays(city_code)}

def get_postal_code_json():
    """API endpoint for postal code"""
    country_code = request.args.get('country_code', 'PH')
    city = request.args.get('city')
    
    if not (country_code and city):
        return jsonify({'postal_code': ''})
    
    postal_code = fetch_postal_code(city, country_code)
    return jsonify({'postal_code': postal_code})