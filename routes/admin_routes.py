from flask import Blueprint, render_template, request, jsonify, session, url_for, flash, redirect
from utilities.login import load_users_from_db
from functools import wraps
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path
from utilities.checkout import get_all_orders, get_order_stats
from utilities.handle_products import handle_add_non_book_product
from utilities.admin import admin_required


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    books = load_books()
    non_books = load_nonbooks()
    users_data = load_users_from_db()

    total_orders, total_revenue = get_order_stats()
    
    total_products = len(books) + len(non_books)
    total_users = len(users_data)
    
    return render_template('components/admin_dashboard.html', 
                        total_products=total_products,
                        total_users=total_users,
                        total_orders=total_orders,
                        total_revenue=total_revenue)

@admin_bp.route('/admin_orders', methods=['GET', 'POST'])
def admin_orders():
    orders = get_all_orders()
    total_orders, total_revenue = get_order_stats()
    return render_template('components/admin_orders.html', 
                            orders=orders, 
                            total_orders=total_orders, 
                            total_revenue=total_revenue)

@admin_bp.route('/admin_products')
@admin_bp.route('/admin_products/<product_type>')
@admin_required
def admin_products(product_type='books'):
    if product_type.lower() == 'books':
        products = load_books()
        for product in products:
            product['image_path'] = get_books_image_path(product['Product ID'])
        return render_template('components/admin_products.html', products=products, product_type='Books')
    elif product_type.lower() == 'non-books':
        products = load_nonbooks()
        for product in products:
            product['image_path'] = get_nonbook_image_path(product['Product ID'])
        return render_template('components/admin_products.html', products=products, product_type='Non-Books')
    else:
        return "Invalid product type", 404

@admin_bp.route('/admin_products2', methods=['GET', 'POST'])
@admin_required
def admin_products2():
    """Complete Non-Books Management Page"""
    if request.method == 'POST':
        return handle_add_non_book_product()
    
    # Get ALL non-books for management
    non_books = load_nonbooks()
    
    # Add image paths
    for nb in non_books:
        nb['image_path'] = get_nonbook_image_path(nb['Product ID'])
    
    # Sort by Product ID (newest first)
    non_books.sort(key=lambda x: x.get('Product ID', 0), reverse=True)
    
    return render_template('components/admin_products2.html', non_book_products=non_books)

def handle_stock_update():
    """Handle stock update requests"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        new_stock = data.get('new_stock')
        
        # Update database
        from database_connection.connector import get_nonbooks_db
        
        with get_nonbooks_db() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE non_books SET quantity = ? WHERE product_id = ?', 
                        (new_stock, product_id))
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
@admin_bp.route('/admin_registeredUsers', methods=['GET', 'POST'])
@admin_required
def admin_registeredUsers():
    users_data = load_users_from_db()
    return render_template('components/admin_registeredUsers.html', users=users_data)

@admin_bp.route('/admin', methods=['GET'])
def admin_login_page():
    """Display admin login page"""
    # If already logged in as admin, redirect to dashboard
    if 'user' in session and session.get('user', {}).get('is_admin'):
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('adminlogin.html')


@admin_bp.route('/admin', methods=['POST'])
def admin_login():
    """Simple admin authentication endpoint using form data"""
    try:
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Debug output
        print(f"Login attempt for: {email}")
        
        # Use the simplified check function
        from utilities.admin import check_admin_login
        
        if check_admin_login(email, password):
            # Set admin session
            session['user'] = {
                'user_id': 0,
                'username': 'Administrator',
                'email': email,
                'is_admin': True
            }
            
            # Redirect to dashboard on success
            return redirect(url_for('admin.admin_dashboard'))
        else:
            # Show login page with error on failure
            flash('Invalid email or password', 'error')
            return render_template('adminlogin.html', error='Invalid email or password')
            
    except Exception as e:
        print(f"Admin login error: {e}")
        import traceback
        traceback.print_exc()
        return render_template('adminlogin.html', error=f'Error: {str(e)}')

@admin_bp.route('/api/update_order_status', methods=['POST'])
@admin_required
def update_order_status():
    if 'user' not in session or session['user'].get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    order_id = request.json.get('order_id')
    new_status = request.json.get('status')
    
    from utilities.checkout import update_order_status
    success = update_order_status(order_id, new_status)
    
    return jsonify({'success': success})

@admin_bp.route('/admin/delete_product', methods=['POST'])
@admin_required
def delete_product():
    """Delete a product from the database"""
    if 'user' not in session or session['user'].get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    product_id = request.json.get('product_id')
    product_type = request.json.get('product_type')
    
    try:
        # Determine which database to use
        db_name = 'books.db' if product_type == 'books' else 'nonbooks.db'
        
        from utilities.checkout import get_db_connection
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        
        # Delete the product (you'll need to know your table structure)
        # This is a placeholder - adjust based on your actual table names
        table_name = 'books' if product_type == 'books' else 'nonbooks'
        cursor.execute(f'DELETE FROM {table_name} WHERE "Product ID" = ?', (product_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting product: {e}")
        return jsonify({'success': False, 'message': str(e)})
    
@admin_bp.route('/get-order-details/<order_id>', methods=['GET'])
@admin_required
def get_order_details(order_id):
    """Get details for a specific order in JSON format for the admin modal"""
    try:
        # Get order from database
        from utilities.order import get_order_by_id
        order = get_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Get items for this order
        order_items = []
        
        # Try to get items from order_items in books.db
        try:
            from database_connection.connector import get_db_connection
            
            # Query books.db for items
            conn = get_db_connection('books.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT product_id, product_name, price, quantity 
                FROM order_items WHERE order_id = ?
            """, (order_id,))
            book_items = cursor.fetchall()
            conn.close()
            
            # Add book items to order_items list
            for item in book_items:
                product_id, product_name, price, quantity = item
                # Simplified image path
                image_path = f"/static/images/Books_Images/fiction_images/{product_id}_Front.jpg"
                order_items.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'price': float(price),
                    'quantity': quantity,
                    'image_path': image_path
                })
        except Exception as e:
            print(f"Error getting book items: {e}")
            
        # Add placeholder items if nothing found
        if not order_items:
            order_items = [{
                'product_id': '1000',
                'product_name': f'Sample Product for Order #{order_id}',
                'price': float(order.get('total_amount', 0) or 0),
                'quantity': 1,
                'image_path': '/static/images/placeholder.jpg'
            }]
        
        # Assign items to order
        order['items'] = order_items
        
        return jsonify(order)
        
    except Exception as e:
        print(f"Error getting order details: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    