from flask import Blueprint, render_template, request, jsonify, session, url_for, flash, redirect
from utilities.login import load_users_from_db
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path
from utilities.checkout import get_all_orders, get_order_stats
from utilities.admin import admin_required
from utilities.handle_products import get_all_products, delete_product as delete_product_function
from utilities.handle_products import add_product, get_order_items, update_product
import time
from utilities.order import get_order_by_id

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    # Use original load_books/load_nonbooks functions
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


@admin_bp.route('/admin/books')
@admin_required
def admin_books():
    """Admin books management page with proper image paths"""
    try:
        # Use the original function that works
        products = load_books()
        
        # Add image paths using the specialized function from load_items.py
        for product in products:
            product_id = product.get('Product ID')
            if product_id:
                product['image_path'] = get_books_image_path(product_id)
        
        return render_template('components/admin_products.html', 
                             products=products, 
                             product_type='Books')
    except Exception as e:
        print(f"Error in admin_books route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading books: {str(e)}"

@admin_bp.route('/admin/non-books')
@admin_required
def admin_non_books():
    """Admin non-books management page with proper image paths"""
    try:
        # Use the original function that works
        products = load_nonbooks()
        
        # Add image paths using the specialized function from load_items.py
        for product in products:
            product_id = product.get('Product ID')
            if product_id:
                product['image_path'] = get_nonbook_image_path(product_id)
        
        return render_template('components/admin_products.html', 
                             products=products, 
                             product_type='Non-Books')
    except Exception as e:
        print(f"Error in admin_non_books route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading non-books: {str(e)}"

# Also update the advanced non-books view
@admin_bp.route('/admin/non-books/advanced', methods=['GET'])
@admin_required
def admin_non_books_advanced():
    """Advanced non-books management with search, filtering"""
    try:
        search = request.args.get('search', '')
        category = request.args.get('category')
        
        # Get all non-books
        all_products = load_nonbooks()
        
        # Add image paths using the specialized function
        for product in all_products:
            product_id = product.get('Product ID')
            if product_id:
                product['image_path'] = get_nonbook_image_path(product_id)
        
        # Filter by search term if provided
        if search:
            filtered_products = []
            search = search.lower()
            for product in all_products:
                if (search in product.get('Product Name', '').lower() or
                    search in product.get('Brand', '').lower() or
                    search in product.get('Product Description', '').lower()):
                    filtered_products.append(product)
            all_products = filtered_products
            
        # Filter by category if provided
        if category:
            filtered_products = []
            for product in all_products:
                if product.get('Category') == category:
                    filtered_products.append(product)
            all_products = filtered_products
        
        # Get unique categories for the filter dropdown
        categories = set()
        for product in load_nonbooks():
            if product.get('Category'):
                categories.add(product.get('Category'))
        
        return render_template(
            'components/admin_products2.html', 
            non_book_products=all_products,
            categories=sorted(list(categories)),
            search=search,
            category=category
        )
    except Exception as e:
        print(f"Error in admin_non_books_advanced route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading advanced non-books view: {str(e)}"

# Add this route to maintain backward compatibility
@admin_bp.route('/admin_products')
@admin_bp.route('/admin_products/<product_type>')
@admin_required
def admin_products(product_type='books'):
    """Legacy route for compatibility - redirects to the new specific routes"""
    if product_type.lower() == 'books':
        return redirect(url_for('admin.admin_books'))
    elif product_type.lower() == 'non-books':
        return redirect(url_for('admin.admin_non_books'))
    else:
        return "Invalid product type", 404

# Add this route for backward compatibility
@admin_bp.route('/admin_products2', methods=['GET'])
@admin_required
def admin_products2():
    """Legacy route for compatibility - redirects to advanced non-books page"""
    return redirect(url_for('admin.admin_non_books_advanced', **request.args))

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
def delete_product_route():
    """Delete a product from the database"""
    if 'user' not in session or not session.get('user', {}).get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    product_id = request.json.get('product_id')
    product_type = request.json.get('product_type')
    
    # Convert product_type to match expected format
    db_product_type = 'book' if product_type == 'books' else 'non_book'
    
    # Use the imported function with a different name
    result = delete_product_function(product_id, db_product_type)
    return jsonify(result)
    
@admin_bp.route('/get-order-details/<order_id>', methods=['GET'])
@admin_required
def get_order_details(order_id):
    """Get details for a specific order in JSON format for the admin modal"""
    try:
        order = get_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order_items = get_order_items(order_id)
        
        # Assign items to order
        order['items'] = order_items
        
        return jsonify(order)
        
    except Exception as e:
        print(f"Error getting order details: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# Add these new routes for product management

@admin_bp.route('/admin/add_product', methods=['POST'])
@admin_required
def add_product_route():
    """Add a new product to the database"""
    try:
        product_type = request.form.get('product_type')
        
        # Process uploaded files for product images
        front_image = request.files.get('front_image')
        back_image = request.files.get('back_image')
        
        # Save images and get filenames
        front_image_filename = None
        back_image_filename = None
        
        if front_image and front_image.filename:
            # Code to save front image
            front_image_filename = f"{product_type}_{int(time.time())}_front.jpg"
            front_image.save(f"static/images/{'Books_Images' if product_type == 'book' else 'Non_Books_Images'}/{front_image_filename}")
        
        if back_image and back_image.filename:
            # Code to save back image
            back_image_filename = f"{product_type}_{int(time.time())}_back.jpg"
            back_image.save(f"static/images/{'Books_Images' if product_type == 'book' else 'Non_Books_Images'}/{back_image_filename}")
        
        # Collect form data
        product_data = {}
        for field in request.form:
            if field != 'product_type':
                product_data[field] = request.form[field]
                
        # Add image filenames to product data
        if front_image_filename:
            product_data['product_image_front'] = front_image_filename
        if back_image_filename:
            product_data['product_image_back'] = back_image_filename
            
        # Use handle_products function
        result = add_product(product_data, product_type)
        
        if result['success']:
            flash('Product added successfully!', 'success')
        else:
            flash(f'Failed to add product: {result.get("error")}', 'error')
            
        return redirect(url_for('admin.admin_products', product_type=f"{product_type}s"))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.admin_products'))

@admin_bp.route('/admin/update_product/<product_id>', methods=['POST'])
@admin_required
def update_product_route(product_id):
    """Update an existing product"""
    try:
        product_type = request.form.get('product_type')
        
        # Collect form data
        product_data = {}
        for field in request.form:
            if field not in ['product_type', 'product_id']:
                product_data[field] = request.form[field]
        
        result = update_product(product_id, product_data, product_type)
        
        if result['success']:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': result.get('error')})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    

@admin_bp.route('/admin_orders')
@admin_required
def admin_orders():
    """Admin orders management page"""
    try:
        # Get all orders for admin view
        orders = get_all_orders()
        return render_template('components/admin_orders.html', orders=orders)
    except Exception as e:
        print(f"Error in admin_orders route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading orders: {str(e)}"