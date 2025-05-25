from forms import RegistrationForm
from api import get_user_country, fetch_provinces, fetch_cities, fetch_barangays, fetch_postal_code
from utilities.storage import load_users, save_users
from flask import render_template, request, redirect, url_for, jsonify, session

def handle_register():
    form = RegistrationForm(request.form)
    get_country = get_user_country()
    form.country.choices = [
        ("void", "--Select country--"),
        ("PH", get_country)
    ]
    form.country.default = "void"
    form.process()

    provinces = fetch_provinces()
    form.province.choices = [("void", "--Select the province--")] + sorted(
        [(province['code'], province['name']) for province in provinces],
        key=lambda x: x[1].lower())
    form.city.choices = [("void", "--Select the city--")]
    form.barangay.choices = [("void", "--Select the barangay--")]

    # ...existing code...
    if request.method == 'POST' and form.validate():
        city_code = form.city.data
        postal_code = None
        if city_code:
            cities = fetch_cities(form.province.data)
            for city in cities:
                if city[0] == city_code:
                    postal_code = city[2]
                    break
            form.postal_code.data = postal_code

        users = load_users()
        username = form.username.data
        password = form.password.data

        for user in users:
            if user['username'] == username:
                return "Username already exists. Try another one."

        new_user = {
            "id": len(users) + 1,
            "username": username,
            "password": password,
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
        users.append(new_user)
        save_users(users)
        return redirect(url_for('login'))

    return render_template('register.html', registration_form=form)

def get_cities_json(province_code):
    cities = fetch_cities(province_code)
    return {"cities": cities}

def get_barangays_json(city_code):
    barangays = fetch_barangays(city_code)
    return {"barangays": barangays}

def get_postal_code_json():
    country_code = request.args.get('country_code', 'PH')
    city = request.args.get('city')
    if not (country_code and city):
        return jsonify({'postal_code': ''})
    postal_code = fetch_postal_code(city, country_code)
    return jsonify({'postal_code': postal_code})