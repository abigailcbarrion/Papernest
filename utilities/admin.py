import json
import os
from functools import wraps
from flask import session, redirect, url_for, flash

def load_admin_credentials():
    """Load admin credentials from JSON file"""
    try:
        admin_file_path = os.path.join('data', 'admin.json')
        with open(admin_file_path, 'r') as file:
            data = json.load(file)
            return data.get('admins', [])
    except Exception as e:
        print(f"Error loading admin credentials: {e}")
        return []

def check_admin_login(email, password):
    """Check if the provided admin credentials are valid"""
    try:
        import json
        import os
        
        # Path to admin credentials file
        admin_file_path = os.path.join('data', 'admin.json')
        
        # Load admin credentials
        with open(admin_file_path, 'r') as file:
            data = json.load(file)
            admins = data.get('admins', [])
            
            # Check if credentials match any admin
            for admin in admins:
                if admin.get('email') == email and admin.get('password') == password:
                    return True
                    
            return False
            
    except Exception as e:
        print(f"Error checking admin login: {e}")
        return False

def admin_required(f):
    """Simple decorator to require admin access for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session.get('user', {}).get('is_admin'):
            flash('Admin access required', 'error')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function