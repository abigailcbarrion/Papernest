from flask import Blueprint, render_template, request, jsonify, session
from utilities.login import load_users_from_db
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    books = load_books()
    non_books = load_nonbooks()
    users_data = load_users_from_db()
    
    total_products = len(books) + len(non_books)
    total_users = len(users_data)
    
    return render_template('components/admin_dashboard.html', 
                        total_products=total_products,
                        total_users=total_users)

@admin_bp.route('/admin_orders', methods=['GET', 'POST'])
def admin_orders():
    return render_template('components/admin_orders.html')

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
    return render_template('components/admin_products2.html')

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