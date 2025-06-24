import sqlite3
import json
import uuid
from datetime import datetime
from flask import session
from database_connection.connector import get_db_connection
from utilities.cart import get_cart_items
from utilities.user_management import get_user_by_id

def get_orders_db():
    """Get a connection to the database containing orders table"""
    return get_db_connection('users.db')

def save_order_to_database(order):
    """Save an order to the database using the correct schema
    
    Args:
        order (dict): The order details to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if 'user' not in session:
            print("[DEBUG] No user in session")
            return False
            
        conn = get_orders_db()
        cursor = conn.cursor()
        
        # Get user information - more carefully
        user = session.get('user', {})
        user_id = user.get('id') if user else None  # Safely get user_id
        username = user.get('username', 'Unknown')
        
        if not user_id:
            print("[DEBUG] No user ID found in session")
            return False
        
        print(f"[DEBUG] User ID: {user_id}, Username: {username}")
        
        # Calculate totals
        items = order.get('items', [])
        subtotal = sum(float(item.get('price', 0)) * int(item.get('quantity', 1)) for item in items)
        shipping_cost = order.get('shipping_cost', 0)
        total_amount = subtotal + shipping_cost
        
        # Get payment method
        payment_method = order.get('payment_method', 'Unknown')
        
        # Insert into orders table according to the actual schema
        cursor.execute('''
            INSERT INTO orders (
                user_id, username, subtotal, shipping_cost, 
                total_amount, payment_method, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            username,
            subtotal,
            shipping_cost,
            total_amount,
            payment_method,
            'pending'
        ))
        
        # Get the auto-incremented order_id
        order_id = cursor.lastrowid
        print(f"[DEBUG] Generated order ID: {order_id}")
        
        # Create order_items table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id VARCHAR(50),
            product_name VARCHAR(200),
            product_type VARCHAR(20),
            price DECIMAL(10,2),
            quantity INTEGER DEFAULT 1,
            subtotal DECIMAL(10,2),
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
        ''')
        
        # Insert items into order_items table
        for item in items:
            item_price = float(item.get('price', 0))
            item_quantity = int(item.get('quantity', 1))
            item_subtotal = item_price * item_quantity
            
            cursor.execute('''
                INSERT INTO order_items (
                    order_id, product_id, product_name, product_type,
                    price, quantity, subtotal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id,
                str(item.get('product_id', '')),  # Convert to string to be safe
                item.get('product_name', ''),
                item.get('product_type', 'product'),
                item_price,
                item_quantity,
                item_subtotal
            ))
            
        # Save changes
        conn.commit()
        conn.close()
        
        # Store order ID in the original order object (for reference)
        order['order_id'] = order_id
        
        print(f"[DEBUG] Order {order_id} saved successfully")
        return True
    except Exception as e:
        print(f"Error saving order: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full error traceback
        return False

def get_order_by_id(order_id):
    """Get an order by its ID using the correct schema
    
    Args:
        order_id (int/str): The order ID to lookup
        
    Returns:
        dict or None: The order details or None if not found
    """
    try:
        conn = get_orders_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get order main details
        cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        order_data = cursor.fetchone()
        
        if not order_data:
            return None
        
        # Convert to dictionary
        order = dict(order_data)
        
        # Get order items
        try:
            cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
            items_data = cursor.fetchall()
            items = [dict(item) for item in items_data]
            order['items'] = items
        except sqlite3.OperationalError:
            # If order_items table doesn't exist
            order['items'] = []
        
        # Get user info for shipping address
        user_id = order['user_id']
        user = get_user_by_id(user_id)
        if user:
            order['shipping_info'] = {
                'method': 'standard',
                'address': f"{user.get('street', '')}, {user.get('barangay', '')}, {user.get('city', '')}, {user.get('province', '')}, {user.get('postal_code', '')}"
            }
        else:
            order['shipping_info'] = {'method': 'standard', 'address': ''}
        
        conn.close()
        return order
    except Exception as e:
        print(f"Error getting order: {str(e)}")
        return None

def get_user_orders_from_db(user_id):
    """Get all orders for a specific user using the correct schema
    
    Args:
        user_id (int): The user ID to get orders for
        
    Returns:
        list: A list of order dictionaries
    """
    try:
        print(f"[DEBUG] Found user_id: {user_id}")
        conn = get_orders_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all orders for this user
        cursor.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC', (user_id,))
        orders_data = cursor.fetchall()
        
        print(f"[DEBUG] Found {len(orders_data)} orders for user {user_id}")
        
        orders = []
        for order_data in orders_data:
            # Get basic order info
            order = dict(order_data)
            
            # Get order items
            try:
                cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order['order_id'],))
                items_data = cursor.fetchall()
                items = [dict(item) for item in items_data]
                order['items'] = items
            except sqlite3.OperationalError:
                # If order_items table doesn't exist
                order['items'] = []
            
            # Add shipping info
            user = get_user_by_id(user_id)
            if user:
                order['shipping_info'] = {
                    'method': 'standard',
                    'address': f"{user.get('street', '')}, {user.get('barangay', '')}, {user.get('city', '')}, {user.get('postal_code', '')}"
                }
            else:
                order['shipping_info'] = {'method': 'standard', 'address': ''}
                
            orders.append(order)
        
        conn.close()
        return orders
    except Exception as e:
        print(f"Error getting user orders: {str(e)}")
        return []

def process_billing(payment_method, payment_details=None):
    """Process billing information and create an order
    
    Args:
        payment_method (str): The selected payment method
        payment_details (str): Additional payment details as JSON
        
    Returns:
        dict: Result of the billing processing
    """
    try:
        if 'user' not in session:
            return {'success': False, 'error': 'User not logged in'}
        
        user = session['user']
        user_id = user.get('id')
        
        # Get cart items
        cart_items, total_amount = get_cart_items()
        print(f"[DEBUG] Total amount: {total_amount}")
        
        if not cart_items:
            return {'success': False, 'error': 'Your cart is empty'}
        
        # Parse payment details if provided
        payment_method_name = payment_method
        if payment_details:
            try:
                payment_info = json.loads(payment_details)
                payment_method_name = payment_info.get('method', payment_method)
            except:
                pass
        
        # Create order
        order = {
            'items': cart_items,
            'subtotal': total_amount,
            'shipping_cost': 0,  # You could calculate this based on address, etc.
            'total_amount': total_amount,
            'payment_method': payment_method_name,
            'status': 'pending'
        }
        
        # Save order to database
        if save_order_to_database(order):
            # Store order ID in session for reference
            session['last_order_id'] = order.get('order_id')
            session['last_order_payment'] = payment_method_name
            return {'success': True, 'order_id': order.get('order_id')}
        else:
            return {'success': False, 'error': 'Failed to save order to database'}
        
    except Exception as e:
        print(f"Error processing billing: {str(e)}")
        return {'success': False, 'error': f'An error occurred: {str(e)}'}

# Fix the clear_cart function to use the correct database
def clear_cart():
    """Clear the user's cart after successful order"""
    try:
        if 'user' not in session:
            return False
            
        user_id = session['user']['id']
        
        # Fix: Specify the database to connect to
        conn = get_db_connection('users.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        # If you're also using session-based cart, clear that too
        if 'cart' in session:
            session.pop('cart')
            
        return True
    except Exception as e:
        print(f"Error clearing cart: {str(e)}")
        return False