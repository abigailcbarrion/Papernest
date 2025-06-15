from flask import Blueprint, request, redirect, url_for, session, jsonify
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