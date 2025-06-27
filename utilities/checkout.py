import sqlite3
from datetime import datetime
from flask import session
from utilities.session_utils import get_current_user_id, get_current_username
from utilities.cart import get_cart_items, clear_user_cart
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path
from utilities.cart import get_cart_items
from utilities.cart import clear_user_cart
import json

def get_db_connection(db_name):
    conn = sqlite3.connect(f'data/{db_name}', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def save_order_to_database(order):
    """Save an order to the database using the correct schema"""
    try:
        # Get user from session properly
        if 'user' not in session:
            print("[DEBUG] No user in session")
            return False
            
        user = session.get('user', {})
        
        # Try to get user_id from multiple possible fields in session
        user_id = get_current_user_id()
        
        if not user_id:
            print("[DEBUG] No user ID found in session")
            return False
            
        print(f"[DEBUG] Using user ID from session: {user_id}")
        
        # Get username
        username = get_current_username() or "Customer"
        
        conn = get_db_connection('users.db')
        cursor = conn.cursor()
        
        # Calculate totals
        items = order.get('items', [])
        subtotal = sum(float(item.get('price', 0)) * int(item.get('quantity', 1)) for item in items)
        shipping_cost = order.get('shipping_cost', 0)
        total_amount = subtotal + shipping_cost
        payment_method = order.get('payment_method', 'Unknown')

        cursor.execute('''
            INSERT INTO orders (
                user_id, username, subtotal, shipping_cost, 
                total_amount, payment_method, status, order_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            username,
            subtotal,
            shipping_cost,
            total_amount,
            payment_method,
            'pending',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # Get the auto-incremented order_id
        order_id = cursor.lastrowid
        print(f"[DEBUG] Created order with ID: {order_id}")
        
        # CRITICAL: Make sure we commit the transaction
        conn.commit()
        
        order['order_id'] = order_id  

        # Verify the order was saved
        cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        saved_order = cursor.fetchone()
        if saved_order:
            print(f"[DEBUG] Order {order_id} verified in database!")
        else:
            print(f"[ERROR] Order {order_id} not found after save!")
            
        conn.close()
        
        # Store order ID in the original order object
        order['order_id'] = order_id
        
        return {'success': True, 'order_id': order_id}
    except Exception as e:
        print(f"Error saving order: {str(e)}")
        import traceback
        traceback.print_exc()  # Print detailed error
        return False

def get_order_by_id(order_id):
    """Get complete order from multiple databases"""
    try:
        # Get main order from users.db
        users_conn = get_db_connection('users.db')
        users_cursor = users_conn.cursor()
        
        users_cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        order = users_cursor.fetchone()
        
        if not order:
            return None
        
        order = dict(order)
        
        # Get shipping info
        users_cursor.execute('SELECT * FROM shipping_info WHERE order_id = ?', (order_id,))
        shipping = users_cursor.fetchone()
        order['shipping_info'] = dict(shipping) if shipping else {}
        
        # Get billing info
        users_cursor.execute('SELECT * FROM billing_info WHERE order_id = ?', (order_id,))
        billing = users_cursor.fetchone()
        order['billing_info'] = dict(billing) if billing else {}
        
        users_conn.close()
        
        # Get order items from books.db and nonbooks.db
        order['items'] = []
        
        for db_name in ['books.db', 'nonbooks.db']:
            item_conn = get_db_connection(db_name)
            item_cursor = item_conn.cursor()
            
            item_cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
            items = item_cursor.fetchall()
            
            for item in items:
                order['items'].append(dict(item))
            
            item_conn.close()
        
        return order
        
    except Exception as e:
        print(f"Error getting order: {e}")
        return None

def process_checkout(form_data):
    """Process checkout with shipping and billing info"""
    if 'user' not in session:
        return {'success': False, 'error': 'User not logged in'}
    
    user_id = get_user_id_from_session()
    if not user_id:
        return {'success': False, 'error': 'User ID not found'}
    
    cart_products, total_amount = get_cart_items()
    
    if not cart_products:
        return {'success': False, 'error': 'Cart is empty'}
    
    # Calculate shipping cost
    shipping_method = form_data.get('shipping_method', 'standard')
    shipping_cost = 0 if shipping_method in ['standard', 'pickup'] else 50
    
    # Create order data
    order_data = {
        'user_id': user_id,  # Use the helper function
        'username': session['user']['username'],
        'items': cart_products,
        'subtotal': total_amount,
        'shipping_cost': shipping_cost,
        'total_amount': total_amount + shipping_cost,
        'shipping_info': {
            'method': shipping_method,
            'name': form_data.get('shipping_name'),
            'address': form_data.get('shipping_address'),
            'city': form_data.get('shipping_city'),
            'province': form_data.get('shipping_province'),
            'postal_code': form_data.get('shipping_postal'),
            'phone': form_data.get('shipping_phone')
        },
        'billing_info': {
            'name': form_data.get('billing_name'),
            'address': form_data.get('billing_address'),
            'city': form_data.get('billing_city'),
            'province': form_data.get('billing_province'),
            'postal_code': form_data.get('billing_postal'),
            'phone': form_data.get('billing_phone')
        },
        'payment_method': form_data.get('payment_method'),
        'status': 'pending'
    }
    
    # Save order
    order_id = save_order_to_database(order_data)
    
    if order_id:
        clear_user_cart()
        return {'success': True, 'order_id': order_id}
    else:
        return {'success': False, 'error': 'Failed to save order'}

def get_user_orders_from_db(user_id):
    """Get all orders for a user from existing database"""
    try:
        if user_id is None:
            user_id = get_user_id_from_session()
            if not user_id:
                return []

        conn = get_db_connection('users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC', (user_id,))
        orders = []
        
        for row in cursor.fetchall():
            order = dict(row)
            orders.append(order)
        
        conn.close()
        return orders
        
    except Exception as e:
        print(f"Error getting user orders: {e}")
        return []

def validate_shipping_info(form_data):
    """Validate shipping information"""
    required_fields = ['shipping_name', 'shipping_address', 'shipping_city', 
                    'shipping_province', 'shipping_postal', 'shipping_phone']
    
    errors = []
    for field in required_fields:
        if not form_data.get(field):
            field_name = field.replace('shipping_', '').replace('_', ' ').title()
            errors.append(f"{field_name} is required")
    
    return errors

def update_order_status(order_id, new_status):
    """Update order status"""
    try:
        with get_db_connection('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE orders SET status = ?, updated_date = ? WHERE order_id = ?',
                (new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_id)
            )
            conn.commit()
            print("Rows affected:", cursor.rowcount)
            return cursor.rowcount > 0 
        return True
    except Exception as e:
        print(f"Error updating order status: {e}")
        return False
    
def get_all_orders():
    """Get all orders from database for admin"""
    try:
        conn = get_db_connection('users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT order_id, username, total_amount, order_date, status 
            FROM orders 
            ORDER BY order_date DESC
        ''')
        
        orders = []
        for row in cursor.fetchall():
            orders.append(dict(row))
        
        conn.close()
        return orders
    except Exception as e:
        print(f"Error getting all orders: {e}")
        return []

def get_order_stats():
    """Get order statistics for admin dashboard"""
    try:
        conn = get_db_connection('users.db')
        cursor = conn.cursor()
        
        # Get total orders count
        cursor.execute('SELECT COUNT(*) FROM orders')
        total_orders = cursor.fetchone()[0]
        
        # Get total revenue
        cursor.execute('SELECT SUM(total_amount) FROM orders WHERE status != "cancelled"')
        total_revenue = cursor.fetchone()[0] or 0
        
        conn.close()
        return total_orders, total_revenue
    except Exception as e:
        print(f"Error getting order stats: {e}")
        return 0, 0

def get_user_id_from_session():
    """Helper function to get user ID from session with different possible keys"""
    if 'user' not in session:
        return None
    
    user = session['user']
    if isinstance(user, dict):
        return user.get('id') or user.get('user_id') or user.get('User ID') or user.get('ID')
    
    return None

def process_billing(payment_method, payment_details=None):
    """Process billing information and create an order"""
    try:
        # Check if user is logged in
        if 'user' not in session:
            print("[DEBUG] No user in session for billing")
            return {'success': False, 'error': 'User not logged in'}
        
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
            'shipping_cost': 0,
            'total_amount': total_amount,
            'payment_method': payment_method_name
        }
        
        # Save order to database
        result = save_order_to_database(order)
        
        if result.get('success'):
            order_id = result.get('order_id')
            
            # IMPORTANT: Save each item to the appropriate order_items table
            for item in cart_items:
                save_item_to_order_items(order_id, item)
            
            # Clear cart after successful order
            clear_user_cart()
            
            # Store order ID in session for reference
            session['last_order_id'] = order_id
            return {'success': True, 'order_id': order_id}
        else:
            return {'success': False, 'error': 'Failed to save order to database'}
        
    except Exception as e:
        print(f"Error processing billing: {str(e)}")
        return {'success': False, 'error': f'An error occurred: {str(e)}'}

def save_order_with_user_id(payment_method, user_id, username=None, cart_items=None,**kwargs):
    """Save an order with explicit user ID without relying on session"""
    try:
        print(f"[DEBUG] Processing order for user_id: {user_id}")
        
        # Temporarily set the user ID in session if needed
        original_user = None
        if 'user' in session:
            original_user = session.get('user')
            
        # # Set the user in session temporarily to use with get_cart_items()
        # session['user'] = {'id': user_id, 'user_id': user_id, 'username': username or 'Customer'}
        
        if cart_items is None:
            cart_items, total_amount = get_cart_items()
        else:
            total_amount = sum(item['price'] * item['quantity'] for item in cart_items)

        if not cart_items:
            return {'success': False, 'error': 'Your cart is empty'}

        try:
            cart_items, total_amount = get_cart_items()  # Remove the parameter
            
            if not cart_items:
                return {'success': False, 'error': 'Your cart is empty'}
            
            # Create order object
            order = {
                'user_id': user_id,
                'username': username or 'Customer',
                'items': cart_items,
                'subtotal': total_amount,
                'shipping_cost': 0,
                'total_amount': total_amount,
                'payment_method': payment_method
            }
            
            db_path = 'data/users.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                # Insert order
                cursor.execute('''
                    INSERT INTO orders (
                        user_id, username, subtotal, shipping_cost,
                        total_amount, payment_method, status, order_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    username or 'Customer',
                    total_amount,
                    0,
                    total_amount,
                    payment_method,
                    'pending',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
                # Get order ID
                order_id = cursor.lastrowid
                print(f"[DEBUG] Created order with ID: {order_id}")
                
                # Commit transaction
                conn.commit()

                # After successfully creating the order
                for item in cart_items:
                    save_item_to_order_items(order_id, item)
                    # Update product stock
                    update_product_stock(
                        item.get('product_id'),
                        item.get('product_type', 'book'),
                        item.get('quantity', 1)
                    )

                clear_user_cart()
                
                return {'success': True, 'order_id': order_id}
                
            except Exception as e:
                print(f"[ERROR] Database error: {str(e)}")
                return {'success': False, 'error': str(e)}
                
            finally:
                conn.close()
                
        finally:
            # Restore original user in session if there was one
            if original_user:
                session['user'] = original_user
            elif 'user' in session:
                session.pop('user')
    
    except Exception as e:
        print(f"[ERROR] Order processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def save_order_items(order_id, items):
    """Save order items to the appropriate database"""
    for item in items:
        product_id = item.get('product_id')
        product_type = item.get('product_type', 'book')
        product_name = item.get('product_name')
        price = item.get('price', 0)
        quantity = item.get('quantity', 1)
        subtotal = price * quantity
        
        # Determine which database to use based on product type
        db_name = 'books.db' if product_type.lower() == 'book' else 'non_books.db'
        
        try:
            conn = get_db_connection(db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO order_items (
                    order_id, product_id, product_name, product_type,
                    price, quantity, subtotal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id,
                product_id,
                product_name,
                product_type,
                price,
                quantity,
                subtotal
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving order item {product_id} to {db_name}: {str(e)}")

# Add this to utilities/checkout.py

def process_billing_fixed(payment_method, payment_details=None):
    """Process billing with fixed database saving"""
    try:
        # Get user ID
        user_id = get_current_user_id()
        
        if not user_id:
            return {'success': False, 'error': 'User not logged in'}
            
        print(f"[DEBUG] Processing billing for user_id: {user_id}")
        
        # Get cart items
        from utilities.cart import get_cart_items, clear_user_cart
        cart_items, total_amount = get_cart_items()
        
        if not cart_items:
            return {'success': False, 'error': 'Your cart is empty'}
        
        # Create order object
        order = {
            'items': cart_items,
            'subtotal': total_amount,
            'shipping_cost': 0,
            'total_amount': total_amount,
            'payment_method': payment_method
        }
        
        # Save order to database
        order_result = save_order_to_database(order)
        
        if order_result.get('success'):
            order_id = order_result.get('order_id')
            
            # IMPORTANT: Save each item to the appropriate order_items table
            for item in cart_items:
                save_item_to_order_items(order_id, item)
            
            # Clear cart
            clear_user_cart()
            
            return {'success': True, 'order_id': order_id}
        else:
            return {'success': False, 'error': 'Failed to save order'}
        
    except Exception as e:
        print(f"[ERROR] Billing processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def save_item_to_order_items(order_id, item):
    """Save an individual item to the appropriate order_items table"""
    try:
        product_id = item.get('product_id')
        product_type = item.get('product_type', 'book')
        product_name = item.get('product_name')
        price = float(item.get('price', 0))
        quantity = int(item.get('quantity', 1))
        subtotal = price * quantity
        
        # Determine which database to use
        db_name = 'books.db' if product_type.lower() == 'book' else 'non_books.db'
        
        # Connect to appropriate database
        from database_connection.connector import get_db_connection
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        
        # Insert the item
        cursor.execute('''
            INSERT INTO order_items (
                order_id, product_id, product_name, product_type,
                price, quantity, subtotal
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            product_id,
            product_name,
            product_type,
            price,
            quantity,
            subtotal
        ))
        
        conn.commit()
        conn.close()
        
        print(f"[DEBUG] Saved item {product_id} to {db_name} order_items table")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to save item {item.get('product_id')} to order_items: {str(e)}")
        return False
    
def update_product_stock(product_id, product_type, quantity):
    """
    Decrement product stock after order placement
    
    Args:
        product_id: ID of the product
        product_type: 'book' or 'nonbook'
        quantity: quantity ordered
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Determine which database to use
        db_name = 'books.db' if product_type.lower() == 'book' or product_type.lower() == 'books' else 'non_books.db'

        # Connect to appropriate database
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        
        # Different table structures for books vs non-books
        if product_type.lower() == 'book':
            # Get current stock
            cursor.execute('SELECT stock_quantity FROM inventory WHERE "Product ID" = ?', (product_id,))
            result = cursor.fetchone()
            
            if result:
                current_stock = result['stock_quantity']
                new_stock = max(0, current_stock - quantity)  # Prevent negative stock
                
                # Update stock
                cursor.execute('UPDATE inventory SET stock_quantity = ? WHERE "Product ID" = ?', 
                            (new_stock, product_id))
                print(f"[STOCK] Updated book #{product_id} stock: {current_stock} → {new_stock}")
        else:
            # For non-books
            cursor.execute('SELECT stock_quantity FROM inventory WHERE id = ?', (product_id,))
            result = cursor.fetchone()
            
            if result:
                current_stock = result['stock_quantity']
                new_stock = max(0, current_stock - quantity)  # Prevent negative stock
                
                # Update stock
                cursor.execute('UPDATE inventory SET stock_quantity = ? WHERE id = ?', 
                            (new_stock, product_id))
                print(f"[STOCK] Updated nonbook #{product_id} stock: {current_stock} → {new_stock}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update stock for product {product_id}: {str(e)}")
        return False