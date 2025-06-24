from flask import Blueprint, render_template, request, jsonify, session, url_for, flash, redirect
from utilities.login import load_users_from_db
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path
from utilities.checkout import get_all_orders, get_order_stats
from utilities.admin import admin_required
from utilities.handle_products import get_all_products, get_current_stock, update_product_inventory, delete_product as delete_product_function
from utilities.handle_products import add_product, get_order_items, update_product
import time
from utilities.order import get_order_by_id
from constants import NORMALIZE_BOOK_CATEGORIES, NORMALIZE_NON_BOOK_CATEGORIES, CATEGORY_MAPPING

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

@admin_bp.route('/admin/products/advanced', methods=['GET', 'POST'])
@admin_required
def admin_products_advanced():
    """Edit mode for managing books and non-books"""
    try:
        # Get product type from query parameters (default to 'non_books')
        product_type = request.args.get('product_type', 'non_books').lower()
        search = request.args.get('search', '')
        category = request.args.get('category')

        # Load products based on product type
        if product_type == 'books':
            all_products = load_books()
            get_image_path = get_books_image_path
            for product in all_products:
                product['quantity'] = get_current_stock(product['Product ID'], 'book')
            categories = sorted(list(NORMALIZE_BOOK_CATEGORIES))
            # print(f"Product Type: {product_type}")
            # print(f"Categories: {categories}")

        elif product_type == 'non_books' or product_type == 'non-books':
            all_products = load_nonbooks()
            get_image_path = get_nonbook_image_path
            for product in all_products:
                product['quantity'] = get_current_stock(product['Product ID'], 'non_book')
            categories = sorted(list(NORMALIZE_NON_BOOK_CATEGORIES))
            # print(f"Product Type: {product_type}")
            # print(f"Categories: {categories}")
        else:
            return "Invalid product type", 400
        
        for product in all_products:
            product.setdefault('Product Name', product.get('Book Name', 'N/A'))
            product.setdefault('Category', 'N/A')
            product.setdefault('Price (PHP)', 0)
            product.setdefault('stock_quantity', 0)

        # Add image paths using the appropriate function
        for product in all_products:
            product_id = product.get('Product ID')
            if product_id:
                product['image_path'] = get_image_path(product_id)

        if not all_products:
            flash(f"No {product_type} products found for the given search or category.", "info")

        # Filter by search term if provided
        if search:
            filtered_products = []
            search = search.lower()
            for product in all_products:
                if product_type == 'books':
                    if (search in product.get('Book Name', '').lower() or
                        search in product.get('Author', '').lower() or
                        search in product.get('Product Description', '').lower()):
                        filtered_products.append(product)
                else:  # non_books
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

        # Handle POST request for saving edits
        if request.method == 'POST':
            try:
                data = request.get_json()
                for product in data.get('products', []):
                    product_id = product.get('Product ID')
                    new_data = {
                        'name': product.get('name'),
                        'price': product.get('price'),
                        'stock': product.get('stock'),
                        'category': product.get('category'),
                    }
                    update_product(product_id, new_data, product_type)
                return jsonify({'success': True, 'message': 'Products updated successfully'})
            except Exception as e:
                print(f"Error updating products: {e}")
                return jsonify({'success': False, 'message': str(e)})

        # Render the template for edit mode
        return render_template(
            'components/admin_edit_products.html',
            products=all_products,
            product_type=product_type,
            search=search,
            categories=categories,
            edit_mode=True,
        )
    except Exception as e:
        print(f"Error in admin_products_advanced route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading advanced products view: {str(e)}"

@admin_bp.route('/admin_products')
@admin_bp.route('/admin_products/<product_type>')
@admin_required
def admin_products(product_type='books'):
    """Legacy route for compatibility - redirects to the new specific routes"""
    try:
        if product_type.lower() == 'books':
            products = load_books()
            for product in products:
                product['quantity'] = get_current_stock(product['Product ID'], 'book')
                if product:
                    product['image_path'] = get_books_image_path(product['Product ID'])
            # Pass products to the 'admin_books' route via session or re-render the template
            return render_template('components/admin_products.html', 
                                   products=products, 
                                   product_type='Books')
        elif product_type.lower() == 'non-books' or product_type.lower() == 'non_books':
            products = load_nonbooks()
            for product in products:
                product['quantity'] = get_current_stock(product['Product ID'], 'non_book')
                if product:
                    product['image_path'] = get_nonbook_image_path(product['Product ID'])
            # Pass products to the 'admin_non_books' route via session or re-render the template
            return render_template('components/admin_products.html', 
                                   products=products, 
                                   product_type='Non-Books')
        else:
            return "Invalid product type", 404
    except Exception as e:
        print(f"Error in admin_products route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading products: {str(e)}"

@admin_bp.route('/admin/products/update-stock', methods=['POST'])
@admin_required
def update_stock():
    """Update the stock quantity of a product"""
    try:
        data = request.get_json()
        print(f"Received data for stock update: {data}")
        product_id = data.get('product_id')
        product_type = data.get('product_type')
        new_stock = data.get('new_stock')

        if not product_id or not product_type or new_stock is None:
            return jsonify({'success': False, 'message': 'Invalid data provided'}), 400

        # Update the inventory
        success = update_product_inventory(product_id, product_type, new_stock - get_current_stock(product_id, product_type))

        if success:
            return jsonify({'success': True, 'message': 'Stock updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update stock'}), 500
    except Exception as e:
        print(f"Error updating stock: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while updating stock'}), 500
    
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

@admin_bp.route('/admin/update_order_status', methods=['POST'])
@admin_required
def update_order_status():
    print("Update order status route called")
    order_id = request.json.get('order_id')
    new_status = request.json.get('status')
    
    from utilities.checkout import update_order_status
    success = update_order_status(order_id, new_status)
    
    
    return jsonify({'success': success})

@admin_bp.route('/admin/products/delete', methods=['POST'])
@admin_required
def delete_product_route():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        product_type = data.get('product_type')

        if not product_id or not product_type:
            return jsonify({'success': False, 'message': 'Missing product_id or product_type'}), 400
        # Convert product_type to match expected format in handle_products.py
        db_product_type = 'book' if product_type in ['books', 'book'] else 'non_book'

        result = delete_product_function(product_id, db_product_type)

        if result.get('success'):
            return jsonify({'success': True, 'message': 'Product deleted successfully'})
        else:
            return jsonify({'success': False, 'message': result.get('error', 'Delete failed')}), 500

    except Exception as e:
        print(f"Error deleting product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/admin/get-order-details/<order_id>', methods=['GET'])
@admin_required
def get_order_details(order_id):
    """Get details for a specific order in JSON format for the admin modal"""
    try:
        order = get_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order_items = get_order_items(order_id)
        for item in order_items:
            # Add image path based on product_type
            if item.get('product_type') in ['book', 'books']:
                item['image_path'] = get_books_image_path(item['product_id'])
            else:
                item['image_path'] = get_nonbook_image_path(item['product_id'])
        
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