import sqlite3
from datetime import datetime
from flask import session

def get_db_connection(db_name):
    """Get connection to specific database"""
    conn = sqlite3.connect(f'data/{db_name}')
    conn.row_factory = sqlite3.Row
    return conn

def save_order_to_databases(order_data):
    """Save order across multiple databases"""
    try:
        # Save main order to users.db
        users_conn = get_db_connection('users.db')
        users_cursor = users_conn.cursor()
        
        users_cursor.execute('''
            INSERT INTO orders (user_id, username, subtotal, shipping_cost, total_amount, payment_method, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['user_id'],
            order_data['username'],
            order_data['subtotal'],
            order_data['shipping_cost'],
            order_data['total_amount'],
            order_data['payment_method'],
            order_data['status']
        ))
        
        order_id = users_cursor.lastrowid
        
        # Save shipping info
        shipping = order_data['shipping_info']
        users_cursor.execute('''
            INSERT INTO shipping_info (order_id, method, recipient_name, address, city, province, postal_code, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, shipping['method'], shipping['name'], shipping['address'], 
              shipping['city'], shipping['province'], shipping['postal_code'], shipping['phone']))
        
        # Save billing info
        billing = order_data['billing_info']
        users_cursor.execute('''
            INSERT INTO billing_info (order_id, name, address, city, province, postal_code, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, billing['name'], billing['address'], billing['city'], 
              billing['province'], billing['postal_code'], billing['phone']))
        
        users_conn.commit()
        users_conn.close()
        
        # Save order items to respective databases
        for item in order_data['items']:
            db_name = 'books.db' if item['type'] == 'book' else 'nonbooks.db'
            item_conn = get_db_connection(db_name)
            item_cursor = item_conn.cursor()
            
            item_cursor.execute('''
                INSERT INTO order_items (order_id, product_id, product_name, product_type, price, quantity, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id,
                item.get('Product ID'),
                item.get('Book Name', item.get('Product Name')),
                item['type'],
                item.get('Price (PHP)'),
                item.get('quantity', 1),
                float(item.get('Price (PHP)', 0)) * item.get('quantity', 1)
            ))
            
            item_conn.commit()
            item_conn.close()
        
        return order_id
        
    except Exception as e:
        print(f"Error saving order: {e}")
        return None

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
    
# Add these functions to your checkout.py file:

def get_cart_products():
    """Get cart products with details from session"""
    from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path
    
    cart_items = session.get('cart', [])
    if not cart_items:
        return [], 0
    
    # Load product data
    books = load_books()
    non_books = load_nonbooks()
    
    cart_products = []
    total_amount = 0
    
    for item_id in cart_items:
        # Check if it's a book
        product = next((b for b in books if b.get('Product ID') == item_id), None)
        if product:
            product['image_path'] = get_books_image_path(item_id)
            product['type'] = 'book'
            product['quantity'] = cart_items.count(item_id)  # Count occurrences for quantity
            cart_products.append(product)
            total_amount += float(product.get('Price (PHP)', 0)) * product['quantity']
        else:
            # Check if it's a non-book
            product = next((nb for nb in non_books if nb.get('Product ID') == item_id), None)
            if product:
                product['image_path'] = get_nonbook_image_path(item_id)
                product['type'] = 'non_book'
                product['quantity'] = cart_items.count(item_id)
                cart_products.append(product)
                total_amount += float(product.get('Price (PHP)', 0)) * product['quantity']
    
    return cart_products, total_amount

def process_checkout(form_data):
    """Process checkout with shipping and billing info"""
    if 'user' not in session:
        return {'success': False, 'error': 'User not logged in'}
    
    user_id = get_user_id_from_session()
    if not user_id:
        return {'success': False, 'error': 'User ID not found'}
    
    cart_products, total_amount = get_cart_products()
    
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
    order_id = save_order_to_databases(order_data)
    
    if order_id:
        # Clear cart after successful order
        session['cart'] = []
        session.modified = True
        return {'success': True, 'order_id': order_id}
    else:
        return {'success': False, 'error': 'Failed to save order'}

def get_user_orders_from_db(user_id):
    """Get all orders for a user from existing database"""
    try:
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
        conn = get_db_connection('users.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE orders SET status = ?, updated_date = ? WHERE order_id = ?', 
                    (new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_id))
        
        conn.commit()
        conn.close()
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

def process_billing(form_data):
    """Process billing/payment information"""
    try:
        payment_method = form_data.get('payment')
        
        # Get cart products
        cart_products, total_amount = get_cart_products()
        
        if not cart_products:
            return {'success': False, 'error': 'Cart is empty'}
        
        # For now, just clear the cart and return success
        # You can implement proper order creation later
        session['cart'] = []
        
        # Generate a fake order ID for now
        import random
        order_id = random.randint(1000, 9999)
        
        return {'success': True, 'order_id': order_id}
        
    except Exception as e:
        print(f"Billing processing error: {e}")
        return {'success': False, 'error': 'Failed to process order'}