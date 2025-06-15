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
    """Handle user login with Flask-WTF form validation"""
    try:
        print(f"Login request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        
        # Handle POST request
        if request.method == 'POST':
            print("Processing POST request")
            
            # For AJAX requests, we might need to handle form data differently
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                print("AJAX request detected")
                
                # Get form data directly for AJAX requests
                username = request.form.get('username')
                password = request.form.get('password')
                
                print(f"Username: {username}, Password: {'*' * len(password) if password else None}")
                
                if not username or not password:
                    return jsonify({'success': False, 'message': 'Username and password are required'})
                
                # Authenticate user
                user = authenticate_user(username.strip(), password)
                print(f"Authentication result: {user is not None}")
                
                if user:
                    # Successful login
                    session['user'] = user
                    session.setdefault('cart', [])
                    session.setdefault('wishlist', [])
                    
                    return jsonify({'success': True, 'message': 'Login successful'})
                else:
                    return jsonify({'success': False, 'message': 'Invalid username or password'})
            else:
                # Handle regular form submission with Flask-WTF
                from forms import LoginForm
                form = LoginForm(request.form)
                
                if form.validate():
                    username = form.username.data
                    password = form.password.data
                    
                    user = authenticate_user(username, password)
                    
                    if user:
                        session['user'] = user
                        session.setdefault('cart', [])
                        session.setdefault('wishlist', [])
                        
                        return redirect(url_for('main.index'))
                    else:
                        return redirect(url_for('main.index', error='invalid_credentials'))
                else:
                    return redirect(url_for('main.index', error='validation_error'))
        
        # Handle GET request
        return redirect(url_for('main.index'))
        
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Server error occurred'})
        else:
            return redirect(url_for('main.index', error='server_error'))