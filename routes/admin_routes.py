from flask import Blueprint, render_template, request, jsonify, session, url_for
from utilities.login import load_users_from_db
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path
from utilities.checkout import get_all_orders, get_order_stats
from utilities.handle_products import handle_add_non_book_product


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
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
def admin_registeredUsers():
    users_data = load_users_from_db()
    return render_template('components/admin_registeredUsers.html', users=users_data)

@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    return render_template('adminlogin.html')

@admin_bp.route('/api/update_order_status', methods=['POST'])
def update_order_status():
    if 'user' not in session or session['user'].get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    order_id = request.json.get('order_id')
    new_status = request.json.get('status')
    
    from utilities.checkout import update_order_status
    success = update_order_status(order_id, new_status)
    
    return jsonify({'success': success})

@admin_bp.route('/admin/delete_product', methods=['POST'])
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