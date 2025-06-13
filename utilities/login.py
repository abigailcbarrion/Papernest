from flask import request, redirect, url_for, session, jsonify
from forms import LoginForm
from database_connection.connector import get_users_db
import sqlite3

def row_to_user_dict(row):
    """Convert database row to user dictionary"""
    return {
        'user_id': row['user_id'],
        'username': row['username'],
        'password': row['password'],
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'title': row['title'],
        'birth_date': row['birth_date'],
        'gender': row['gender'],
        'phone_number': row['phone_number'],
        'email': row['email'],
        'country': row['country'],
        'province': row['province'],
        'city': row['city'],
        'barangay': row['barangay'],
        'postal_code': row['postal_code']
    }

def load_users_from_db():
    """Load all users from SQLite database"""
    try:
        with get_users_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            return [row_to_user_dict(row) for row in rows]
    except Exception as e:
        print(f"Error loading users: {e}")
        return []

def authenticate_user(username, password):
    """Authenticate user using database query"""
    try:
        with get_users_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            row = cursor.fetchone()
            return row_to_user_dict(row) if row else None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def handle_login():
    """Handle user login"""
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        
        user = authenticate_user(username, password)
        
        if user:
            # Successful login
            session['user'] = user
            session.setdefault('cart', [])
            session.setdefault('wishlist', [])
            
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Login successful'})
            else:
                return redirect(url_for('index'))
        else:
            # Invalid credentials
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Invalid username or password. Please try again.'})
            else:
                return redirect(url_for('index', error='invalid_credentials'))
    
    # If GET request or form validation fails
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'})
    else:
        return redirect(url_for('index'))