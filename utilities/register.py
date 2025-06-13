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
    """Setup form choices for dropdowns with better error handling"""
    try:
        # Set up country choices
        country = get_user_country()
        form.country.choices = [("void", "--Select country--"), ("PH", country)]
        form.country.default = "void"
        
        # Set up province choices
        print("Fetching provinces...")
        provinces = fetch_provinces()
        print(f"Provinces fetched: {len(provinces) if provinces else 0}")
        
        if provinces:
            form.province.choices = [("void", "--Select the province--")] + sorted(
                [(p['code'], p['name']) for p in provinces], key=lambda x: x[1].lower())
            print(f"Province choices set: {len(form.province.choices)} options")
        else:
            form.province.choices = [("void", "--Select the province--")]
        
        # Initialize city and barangay with default + all possible options for validation
        form.city.choices = [("void", "--Select the city--")]
        form.barangay.choices = [("void", "--Select the barangay--")]
        
        # Pre-populate cities and barangays for validation if needed
        # This is a workaround for form validation - we'll add all possible options
        try:
            all_cities = []
            all_barangays = []
            
            # Get cities for a few common provinces to populate validation options
            common_provinces = ["041000000", "137400000", "072200000"]  # Batangas, Metro Manila, Cebu
            
            for prov_code in common_provinces:
                try:
                    cities = fetch_cities(prov_code)
                    if cities:
                        all_cities.extend([(c['code'], c['name']) for c in cities])
                        
                        # Get barangays for first few cities
                        for city in cities[:3]:  # Limit to first 3 cities per province
                            try:
                                barangays = fetch_barangays(city['code'])
                                if barangays:
                                    all_barangays.extend([(b['code'], b['name']) for b in barangays])
                            except:
                                continue
                except:
                    continue
            
            # Add all possible cities and barangays for validation
            if all_cities:
                form.city.choices.extend(all_cities)
            if all_barangays:
                form.barangay.choices.extend(all_barangays)
                
            print(f"Total city choices: {len(form.city.choices)}")
            print(f"Total barangay choices: {len(form.barangay.choices)}")
            
        except Exception as e:
            print(f"Error pre-populating choices: {e}")
        
        print("Form choices setup completed")
        
    except Exception as e:
        print(f"Error in setup_form_choices: {e}")
        # Set fallback choices
        form.country.choices = [("PH", "Philippines")]
        form.province.choices = [("void", "--Select the province--")]
        form.city.choices = [("void", "--Select the city--")]
        form.barangay.choices = [("void", "--Select the barangay--")]
        
def get_city_name_by_code(province_code, city_code):
    """Get city name from city code"""
    if not city_code or city_code == "void":
        return None
    
    cities = fetch_cities(province_code)
    for city in cities:
        if city['code'] == city_code:
            return city['name']
    return None

def create_user_data(form_data):
    """Create user data dictionary from request form data"""
    return {
        "username": form_data.get('username'),
        "password": form_data.get('password'),
        "first_name": form_data.get('first_name'),
        "last_name": form_data.get('last_name'),
        "title": form_data.get('title', ''),
        "birth_date": form_data.get('birth_date'),
        "gender": form_data.get('gender', ''),
        "phone_number": form_data.get('phone_number'),
        "email": form_data.get('email'),
        "country": form_data.get('country', 'void'),
        "province": form_data.get('province', 'void'),
        "city": form_data.get('city', 'void'),
        "barangay": form_data.get('barangay', 'void'),
        "postal_code": form_data.get('postal_code', '1000')
    }

def handle_register():
    """Handle user registration with form validation and success popup"""
    form = RegistrationForm()
    setup_form_choices(form)

    if request.method == 'POST':
        print("POST request received")
        print(f"Form data: {request.form}")
        
        # Manually populate form data for validation
        form.first_name.data = request.form.get('first_name')
        form.last_name.data = request.form.get('last_name')
        form.title.data = request.form.get('title', '')
        form.birth_date.data = request.form.get('birth_date')
        form.gender.data = request.form.get('gender', '')
        form.phone_number.data = request.form.get('phone_number')
        form.username.data = request.form.get('username')
        form.email.data = request.form.get('email')
        form.password.data = request.form.get('password')
        form.confirm_password.data = request.form.get('confirm_password')
        form.country.data = request.form.get('country', 'void')
        form.province.data = request.form.get('province', 'void')
        
        # For city and barangay, add the submitted values to choices to pass validation
        city_code = request.form.get('city', 'void')
        barangay_code = request.form.get('barangay', 'void')
        
        if city_code != 'void':
            # Add the submitted city to choices if not already there
            city_choices = [choice[0] for choice in form.city.choices]
            if city_code not in city_choices:
                form.city.choices.append((city_code, f"City {city_code}"))
        
        if barangay_code != 'void':
            # Add the submitted barangay to choices if not already there
            barangay_choices = [choice[0] for choice in form.barangay.choices]
            if barangay_code not in barangay_choices:
                form.barangay.choices.append((barangay_code, f"Barangay {barangay_code}"))
        
        form.city.data = city_code
        form.barangay.data = barangay_code
        form.postal_code.data = request.form.get('postal_code', '1000')
        
        # Skip CSRF validation
        form.csrf_token.data = None
        
        # Validate form data
        if form.validate():
            print("Form validation passed")
            
            # Convert codes to names before saving
            form_data_dict = request.form.to_dict()
            
            # Convert country code to name
            country_code = form_data_dict.get('country', 'PH')
            if country_code == 'PH':
                form_data_dict['country'] = 'Philippines'
            
            # Convert province code to name
            province_code = form_data_dict.get('province')
            province_name = get_province_name_by_code(province_code)
            if province_name:
                form_data_dict['province'] = province_name
            
            # Convert city code to name
            city_code = form_data_dict.get('city')
            city_name = get_city_name_by_code(province_code, city_code)
            if city_name:
                form_data_dict['city'] = city_name
            
            # Convert barangay code to name
            barangay_code = form_data_dict.get('barangay')
            barangay_name = get_barangay_name_by_code(city_code, barangay_code)
            if barangay_name:
                form_data_dict['barangay'] = barangay_name
            
            # Get postal code
            if city_name:
                print(f"Fetching postal code for: {city_name}")
                postal_code = fetch_postal_code(city_name, "PH")
                form_data_dict['postal_code'] = postal_code
                print(f"Postal code result: {postal_code}")
            else:
                form_data_dict['postal_code'] = "1000"  # Default postal code

            if check_username_exists(request.form.get('username')):
                print("Username already exists")
                return render_template('register.html', 
                                    registration_form=form, 
                                    error="Username already exists. Try another one.")

            # Use your existing create_user_data function
            user_data = create_user_data(form_data_dict)
            print(f"User data to save: {user_data}")
            
            try:
                database_result = save_user_to_db(user_data)
                print(f"Database save result: {database_result}")
                
                if database_result:
                    print("Registration successful - showing success popup")
                    return render_template('register.html', 
                                        registration_form=form, 
                                        success=True)
                else:
                    print("Database save returned False")
                    return render_template('register.html', 
                                        registration_form=form, 
                                        error="Registration failed. Please try again.")
                    
            except Exception as e:
                print(f"Exception during database save: {e}")
                return render_template('register.html', 
                                    registration_form=form, 
                                    error="Registration failed due to database error.")
        else:
            print(f"Form validation failed: {form.errors}")
            return render_template('register.html', 
                                registration_form=form, 
                                errors=form.errors)

    # Always return a response for GET requests
    return render_template('register.html', registration_form=form)

def get_cities_json(province_code):
    """API endpoint for cities"""
    cities = fetch_cities(province_code)
    return {"cities": cities}

def get_barangays_json(city_code):
    """API endpoint for barangays"""
    barangays = fetch_barangays(city_code)
    return {"barangays": barangays}

def get_postal_code_json():
    """API endpoint for postal code with better error handling"""
    country_code = request.args.get('country_code', 'PH')
    city = request.args.get('city')
    
    if not city:
        return jsonify({'postal_code': '1000'})
    
    try:
        postal_code = fetch_postal_code(city, country_code)
        return jsonify({'postal_code': postal_code})
    except Exception as e:
        print(f"Error in postal code endpoint: {e}")
        return jsonify({'postal_code': '1000'})
    
def get_province_name_by_code(province_code):
    """Get province name from province code"""
    if not province_code or province_code == "void":
        return None
    
    provinces = fetch_provinces()
    for province in provinces:
        if province['code'] == province_code:
            return province['name']
    return None

def get_barangay_name_by_code(city_code, barangay_code):
    """Get barangay name from barangay code"""
    if not barangay_code or barangay_code == "void":
        return None
    
    barangays = fetch_barangays(city_code)
    for barangay in barangays:
        if barangay['code'] == barangay_code:
            return barangay['name']
    return None