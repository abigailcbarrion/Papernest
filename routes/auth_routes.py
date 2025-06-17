from flask import Blueprint, request, redirect, url_for, session, jsonify
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utilities.register import handle_register, get_cities_json, get_barangays_json, get_postal_code_json
from utilities.login import handle_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return handle_register()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return handle_login()

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@auth_bp.route('/get_cities/<province_code>')
def get_cities(province_code):
    return jsonify(get_cities_json(province_code))

@auth_bp.route('/get_barangays/<city_code>')
def get_barangays(city_code):
    return jsonify(get_barangays_json(city_code))

@auth_bp.route('/get_postal_code')
def get_postal_code():
    return get_postal_code_json()

@auth_bp.route('/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    is_authenticated = 'user' in session
    return jsonify({'authenticated': is_authenticated})

@auth_bp.route('/update_address', methods=['GET', 'POST'])
def update_address():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your address.")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Retrieve form data
        updated_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
        'city': request.form.get('city'),
        'barangay': request.form.get('barangay'),
        'province': request.form.get('province'),
        'street': request.form.get('street'),
        'postal_code': request.form.get('postal_code'),
        'country': request.form.get('country'),
        'phone_number': request.form.get('phone_number'),
    }

    # TODO: update your database with `updated_data` using your preferred method (SQLAlchemy or raw SQL)
    # e.g., update_user_address(user_id, updated_data)

    flash("Address updated successfully.")
    return redirect(url_for('main.account'))  # change to your actual account route

# Delete Address Route
@auth_bp.route('/delete_address', methods=['POST'])
def delete_address():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to delete your address.")
        return redirect(url_for('auth.login'))

    # TODO: delete address from DB using user_id
    # e.g., delete_user_address(user_id)

    flash("Address deleted successfully.")
    return redirect(url_for('main.account'))  # change to your actual account route
