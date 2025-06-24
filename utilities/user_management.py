import sqlite3
from database_connection.connector import get_db_connection, get_users_db
import json

def update_user_address(user_id, form_data):
    """Update user's address information"""
    try:
        # Implement your address update logic here
        print(f"Updating address for user {user_id} with data: {form_data}")
        # Add your database update code here
        return True
    except Exception as e:
        print(f"Error updating address: {str(e)}")
        return False

def delete_user_address(user_id):
    """Delete user's address information"""
    try:
        # Implement your address deletion logic here
        print(f"Deleting address for user {user_id}")
        # Add your database deletion code here
        return True
    except Exception as e:
        print(f"Error deleting address: {str(e)}")
        return False

def get_user_by_id(user_id):
    """Retrieve a user from the database by ID
    
    Args:
        user_id (int): The ID of the user to retrieve
        
    Returns:
        dict: User information or None if not found
    """
    try:
        if not user_id:
            print("[DEBUG] No user ID provided to get_user_by_id")
            return None
            
        conn = get_db_connection('users.db')  # Make sure to connect to users.db
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        print(f"[DEBUG] Looking up user with ID: {user_id}")
        
        # Check the column name - might be 'id' or 'user_id'
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        id_column = "id"  # default
        for col in columns:
            if col[1].lower() in ("id", "user_id"):
                id_column = col[1]
                break
                
        print(f"[DEBUG] Using ID column: {id_column}")
        
        # Use the correct column name for the query
        query = f"SELECT * FROM users WHERE {id_column} = ?"
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        
        conn.close()
        
        if user_data:
            # Convert SQLite Row to dictionary
            user = dict(user_data)
            print(f"[DEBUG] Found user: {user.get('username', '')}")
            return user
        else:
            print(f"[DEBUG] No user found with ID {user_id}")
            return None
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full error traceback
        return None

def get_user_by_email(email):
    """Retrieve a user from the database by email
    
    Args:
        email (str): The email of the user to retrieve
        
    Returns:
        dict: User information or None if not found
    """
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        
        conn.close()
        
        if user_data:
            return dict(user_data)
        else:
            return None
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        return None

def get_orders_db():
    """Get a connection to the database containing orders table"""
    return get_db_connection('users.db')

def get_user_orders_from_db(user_id):
    """Get all orders for a specific user
    
    Args:
        user_id (int): The user ID to get orders for
        
    Returns:
        list: A list of order dictionaries
    """
    try:
        print(f"[DEBUG] Finding orders for user_id: {user_id}")
        conn = get_orders_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if the orders table has the expected structure
        cursor.execute("PRAGMA table_info(orders)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"[DEBUG] Orders table columns: {column_names}")
        
        # Now try to get the user's orders
        cursor.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC', (user_id,))
        orders_data = cursor.fetchall()
        
        # Convert to list of dictionaries
        orders = [dict(row) for row in orders_data]
        
        conn.close()
        print(f"[DEBUG] Found {len(orders)} orders for user {user_id}")
        
        return orders
    except Exception as e:
        print(f"Error getting user orders: {str(e)}")
        return []

def update_user_profile(user_id, form_data):
    """Update user profile information
    
    Args:
        user_id (int): The ID of the user to update
        form_data (dict): The new user data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Extract form data
        first_name = form_data.get('first_name', '')
        last_name = form_data.get('last_name', '')
        email = form_data.get('email', '')
        phone = form_data.get('phone', '')
        
        # Update user information
        cursor.execute('''
            UPDATE users 
            SET first_name = ?, last_name = ?, email = ?, phone = ? 
            WHERE id = ?
        ''', (first_name, last_name, email, phone, user_id))
        
        # Update address information if present
        street = form_data.get('street')
        barangay = form_data.get('barangay')
        city = form_data.get('city')
        province = form_data.get('province')
        postal_code = form_data.get('postal_code')
        country = form_data.get('country')
        
        if all([street, city, province, postal_code, country]):
            cursor.execute('''
                UPDATE users 
                SET street = ?, barangay = ?, city = ?, province = ?, postal_code = ?, country = ? 
                WHERE id = ?
            ''', (street, barangay, city, province, postal_code, country, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating user profile: {str(e)}")
        return False