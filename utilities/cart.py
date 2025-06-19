import sqlite3
from flask import session
from datetime import datetime
from utilities.session_utils import get_current_user_id
from utilities.load_items import get_books_image_path, get_nonbook_image_path
from database_connection.connector import get_users_db, get_books_db, get_nonbooks_db

def add_to_cart_data(product_id, product_type, quantity=1, **kwargs):
    """Add item to user's cart in database"""
    user_id = get_current_user_id()

    product_name = kwargs.get('product_name', 'Unknown Product')
    price = kwargs.get('price', 0.0)
    image_pat = kwargs.get('image_path')

    print(f"[DEBUG] add_to_cart_data called - user_id: {user_id}, product_id: {product_id}, product_type: {product_type}")
    
    if not user_id:
        return {'success': False, 'message': 'User not logged in'}
    
    try:
        conn = get_users_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"[DEBUG] Database connection established")
        
        # Check if item already exists in cart
        cursor.execute('''
            SELECT cart_id, quantity FROM user_cart 
            WHERE user_id = ? AND product_id = ? AND product_type = ?
        ''', (user_id, str(product_id), product_type))
        
        existing_item = cursor.fetchone()
        print(f"[DEBUG] Existing item check: {existing_item}")
        
        if existing_item:
            # Update quantity if item exists
            new_quantity = existing_item['quantity'] + quantity
            cursor.execute('''
                UPDATE user_cart 
                SET quantity = ?, added_date = CURRENT_TIMESTAMP 
                WHERE cart_id = ?
            ''', (new_quantity, existing_item['cart_id']))
            
            message = f'Updated quantity to {new_quantity}'
            print(f"[DEBUG] Updated existing item to quantity: {new_quantity}")
        else:
            # Insert new item
            cursor.execute('''
                INSERT INTO user_cart (user_id, product_id, product_type, quantity, added_date)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, str(product_id), product_type, quantity))
            
            message = 'Item added to cart'
            print(f"[DEBUG] Inserted new item")
        
        conn.commit()
        
        # Verify the item was added/updated
        cursor.execute('SELECT * FROM user_cart WHERE user_id = ?', (user_id,))
        all_items = cursor.fetchall()
        print(f"[DEBUG] All cart items after operation: {[dict(item) for item in all_items]}")
        
        conn.close()
        
        print(f"[DEBUG] Operation successful: {message}")
        return {'success': True, 'message': message}
        
    except Exception as e:
        print(f"[DEBUG] Error adding to cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': f'Database error: {str(e)}'}

def get_cart_items():
    """Get all cart items for current user with product details"""
    user_id = get_current_user_id()
    print(f"[DEBUG] get_cart_items called - user_id: {user_id}")
    
    if not user_id:
        print("[DEBUG] No user_id, returning empty cart")
        return [], 0.0
    
    try:
        # Get cart items from users database
        users_conn = get_users_db()
        users_conn.row_factory = sqlite3.Row
        users_cursor = users_conn.cursor()
        
        users_cursor.execute('''
            SELECT 
                cart_id,
                product_id,
                product_type,
                quantity,
                added_date
            FROM user_cart
            WHERE user_id = ?
            ORDER BY added_date DESC
        ''', (user_id,))
        
        cart_items = users_cursor.fetchall()
        print(f"[DEBUG] Raw cart items from database: {[dict(item) for item in cart_items]}")
        users_conn.close()
        
        # Get product details for each cart item
        detailed_cart_items = []
        total_amount = 0.0
        
        for item in cart_items:
            print(f"[DEBUG] Processing cart item: {dict(item)}")
            product_details = get_product_details(item['product_id'], item['product_type'])
            print(f"[DEBUG] Product details for {item['product_id']}: {product_details}")
            
            if product_details:
                cart_item = {
                    'cart_id': item['cart_id'],
                    'product_id': item['product_id'],
                    'product_type': item['product_type'],
                    'quantity': item['quantity'],
                    'added_date': item['added_date'],
                    'product_name': product_details.get('product_name', 'Unknown Product'),
                    'price': float(product_details.get('price', 0)),
                    'image_path': product_details.get('image_path', '/static/images/placeholder.png')
                }
                
                detailed_cart_items.append(cart_item)
                total_amount += cart_item['price'] * cart_item['quantity']
                print(f"[DEBUG] Added detailed cart item: {cart_item}")
            else:
                print(f"[DEBUG] No product details found for {item['product_id']} ({item['product_type']})")
        
        print(f"[DEBUG] Final cart items: {detailed_cart_items}")
        print(f"[DEBUG] Total amount: {total_amount}")
        
        return detailed_cart_items, total_amount
        
    except Exception as e:
        print(f"[DEBUG] Error getting cart items: {str(e)}")
        import traceback
        traceback.print_exc()
        return [], 0.0

def get_product_details(product_id, product_type):
    """Get product details from books or non_books database using correct column names"""
    print(f"[DEBUG] get_product_details called - product_id: {product_id}, product_type: {product_type}")
    
    try:
        if product_type == 'book':
            conn = get_books_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Use the actual column names from your database (without quotes)
            cursor.execute('''
                SELECT 
                    product_id,
                    book_name,
                    price_php
                FROM books 
                WHERE product_id = ?
            ''', (int(product_id),))
            
            product = cursor.fetchone()
            conn.close()
            
            if product:
                # Use your existing image path function
                image_path = get_books_image_path(str(product_id), "Product Image Front")
                
                result = {
                    'product_id': product['product_id'],
                    'product_name': product['book_name'],
                    'price': product['price_php'],
                    'image_path': image_path
                }
                print(f"[DEBUG] Book details: {result}")
                return result
                
        else:  # non_book
            conn = get_nonbooks_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Use the actual column names from your database (without quotes)
            cursor.execute('''
                SELECT 
                    product_id,
                    product_name,
                    price_php
                FROM non_books 
                WHERE product_id = ?
            ''', (int(product_id),))
            
            product = cursor.fetchone()
            conn.close()
            
            if product:
                # Use your existing image path function
                image_path = get_nonbook_image_path(str(product_id), "Product Image Front")
                
                result = {
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'price': product['price_php'],
                    'image_path': image_path
                }
                print(f"[DEBUG] Non-book details: {result}")
                return result
        
        print(f"[DEBUG] No product found with ID {product_id}")
        return None
        
    except Exception as e:
        print(f"[DEBUG] Error getting product details: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def update_cart_quantity(product_id, product_type, quantity):
    """Update quantity of item in cart"""
    user_id = get_current_user_id()
    if not user_id:
        return {'success': False, 'message': 'User not logged in'}
    
    try:
        conn = get_users_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if quantity <= 0:
            # Remove item if quantity is 0 or less
            cursor.execute('''
                DELETE FROM user_cart 
                WHERE user_id = ? AND product_id = ? AND product_type = ?
            ''', (user_id, str(product_id), product_type))
            message = 'Item removed from cart'
        else:
            # Update quantity
            cursor.execute('''
                UPDATE user_cart 
                SET quantity = ?, added_date = CURRENT_TIMESTAMP
                WHERE user_id = ? AND product_id = ? AND product_type = ?
            ''', (quantity, user_id, str(product_id), product_type))
            message = f'Quantity updated to {quantity}'
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': message}
        
    except Exception as e:
        print(f"Error updating cart quantity: {str(e)}")
        return {'success': False, 'message': f'Database error: {str(e)}'}

def remove_from_cart_data(product_id, product_type):
    """Remove item from cart"""
    user_id = get_current_user_id()
    if not user_id:
        return {'success': False, 'message': 'User not logged in'}
    
    try:
        conn = get_users_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM user_cart 
            WHERE user_id = ? AND product_id = ? AND product_type = ?
        ''', (user_id, str(product_id), product_type))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'Item removed from cart'}
        
    except Exception as e:
        print(f"Error removing from cart: {str(e)}")
        return {'success': False, 'message': f'Database error: {str(e)}'}

def get_cart_count():
    """Get total number of items in user's cart"""
    user_id = get_current_user_id()
    if not user_id:
        return 0
    
    try:
        conn = get_users_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COALESCE(SUM(quantity), 0) as total_count
            FROM user_cart 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return int(result['total_count']) if result else 0
        
    except Exception as e:
        print(f"Error getting cart count: {str(e)}")
        return 0

def clear_user_cart():
    """Clear all items from user's cart (useful after checkout)"""
    user_id = get_current_user_id()
    if not user_id:
        return {'success': False, 'message': 'User not logged in'}
    
    try:
        conn = get_users_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM user_cart WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'Cart cleared'}
        
    except Exception as e:
        print(f"Error clearing cart: {str(e)}")
        return {'success': False, 'message': f'Database error: {str(e)}'}

def add_to_wishlist_data(product_id, product_type):
    """Add item to user's wishlist"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return {'success': False, 'message': 'User not found'}
        
        print(f"[DEBUG] Adding to wishlist: user_id={user_id}, product_id={product_id}, product_type={product_type}")
        
        conn = get_users_db()
        cursor = conn.cursor()
        
        # Check if wishlist table exists, create if not
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                product_type TEXT NOT NULL,
                added_date TEXT NOT NULL,
                UNIQUE(user_id, product_id, product_type)
            )
        ''')
        
        # Check if item already in wishlist
        cursor.execute('''
            SELECT * FROM wishlist 
            WHERE user_id = ? AND product_id = ? AND product_type = ?
        ''', (user_id, str(product_id), product_type))
        
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'message': 'Item already in wishlist'}
        
        # Add to wishlist
        from datetime import datetime
        cursor.execute('''
            INSERT INTO wishlist (user_id, product_id, product_type, added_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, str(product_id), product_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        
        print(f"[DEBUG] Successfully added to wishlist")
        return {'success': True, 'message': 'Item added to wishlist'}
        
    except Exception as e:
        print(f"Error adding to wishlist: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': str(e)}

def get_wishlist_items():
    """Get all items in user's wishlist"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return []
        
        conn = get_users_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_id, product_type, added_date
            FROM wishlist 
            WHERE user_id = ?
            ORDER BY added_date DESC
        ''', (user_id,))
        
        wishlist_items = cursor.fetchall()
        conn.close()
        
        print(f"[DEBUG] Found {len(wishlist_items)} wishlist items for user {user_id}")
        
        # Get product details for each item   
        detailed_items = []
        for item in wishlist_items:
            print(f"[DEBUG] Getting details for product {item['product_id']}, type: {item['product_type']}")
            product_details = get_product_details(item['product_id'], item['product_type'])
            if product_details:
                product_details['added_date'] = item['added_date']
                product_details['product_type'] = item['product_type']  # Ensure product_type is included
                detailed_items.append(product_details)
                print(f"[DEBUG] Added product details: {product_details['product_name']}")
            else:
                print(f"[DEBUG] No details found for product {item['product_id']}")
        
        print(f"[DEBUG] Returning {len(detailed_items)} detailed wishlist items")
        return detailed_items
        
    except Exception as e:
        print(f"Error getting wishlist items: {str(e)}")
        import traceback
        traceback.print_exc()
        return []  
    
def remove_from_wishlist_data(product_id, product_type):
    """Remove item from user's wishlist"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return {'success': False, 'message': 'User not found'}
        
        print(f"[DEBUG] Removing from wishlist: user_id={user_id}, product_id={product_id}, product_type={product_type}")
        
        conn = get_users_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM wishlist 
            WHERE user_id = ? AND product_id = ? AND product_type = ?
        ''', (user_id, str(product_id), product_type))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            print(f"[DEBUG] Successfully removed from wishlist")
            return {'success': True, 'message': 'Item removed from wishlist'}
        else:
            return {'success': False, 'message': 'Item not found in wishlist'}
        
    except Exception as e:
        print(f"Error removing from wishlist: {str(e)}")
        import traceback
        return {'success': False, 'message': str(e)}