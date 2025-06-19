from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from utilities.load_items import get_books_image_path, get_trending, get_nonbook_image_path
from utilities.storage import get_featured_author
from utilities.cart import get_wishlist_items as get_wishlist, get_cart_items
from utilities.account import get_actual_order_items, generate_representative_items
from utilities.load_items import get_books_image_path
from utilities.user_management import get_user_orders_from_db as get_orders

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/homepage')
def index():
    featured_author = get_featured_author()
    trending_books = get_trending(curr_section='homepage')
    for item in trending_books:
        item['image_path'] = get_books_image_path(item['Product ID'])
    popular_categories = [
        {'name': 'Fiction', 'image': url_for('static', filename='images/popular/books_fiction.png'), 'link': url_for('product.category_products', category_name='fiction')},
        {'name': 'Non-Fiction', 'image': url_for('static', filename='images/popular/books_non_fiction.png'), 'link': url_for('product.category_products', category_name='non-fiction')},
        {'name': 'Art Supplies', 'image': url_for('static', filename='images/popular/nonbooks_art_supplies.png'), 'link': '/category/art-supplies'},
        {'name': 'Calendars and Planners', 'image': url_for('static', filename='images/popular/nonbooks_calendar_planner.png'), 'link': '/category/calendars-and-planners'}
    ]
    return render_template('index.html', 
                        popular_items=trending_books,
                        featured_author=featured_author, 
                        popular_categories=popular_categories,
                        page_type='homepage')

@main_bp.route('/about')
def about():
    return render_template('about_us.html')

@main_bp.route('/help')
def help():
    return render_template('faqs.html')

@main_bp.route('/books')
def books():
    trending_books = get_trending(curr_section='books')
    for item in trending_books:
        item['image_path'] = get_books_image_path(item['Product ID'])
    popular_categories = [
        {'name': "Children's", 'image': url_for('static', filename='images/popular/books_childrens.png'), 'link': url_for('product.category_products', category_name="children's-books")},
        {'name': 'Fiction', 'image': url_for('static', filename='images/popular/books_fiction.png'), 'link': url_for('product.category_products', category_name='fiction')},
        {'name': 'Non-Fiction', 'image': url_for('static', filename='images/popular/books_non_fiction.png'), 'link': url_for('product.category_products', category_name='non-fiction')},
        {'name': 'Self-Help and Development', 'image': url_for('static', filename='images/popular/books_self_help.png'), 'link': url_for('product.category_products', category_name='self-help-and-personal-development')}
    ]
    return render_template('books.html', popular_items=trending_books, page_type='books', popular_categories=popular_categories)

@main_bp.route('/non_books')
def non_books():
    trending_non_books = get_trending(curr_section='non_books')
    for item in trending_non_books:
        item['image_path'] = get_nonbook_image_path(item['Product ID'])
    popular_categories = [
        {'name': 'Art Supplies', 'image': url_for('static', filename='images/popular/nonbooks_art_supplies.png'), 'link': '/category/art-supplies'},
        {'name': 'Calendars and Planners', 'image': url_for('static', filename='images/popular/nonbooks_calendar_planner.png'), 'link': '/category/calendars-and-planners'},
        {'name': 'Notebooks and Journals', 'image': url_for('static', filename='images/popular/nonbooks_notebook_journal.png'), 'link': '/category/notebooks-and-journals'},
        {'name': 'Novelties', 'image': url_for('static', filename='images/popular/nonbooks_novelties.png'), 'link': '/category/novelties'}
    ]
    return render_template('non_books.html', popular_items=trending_non_books, page_type='non_books', popular_categories=popular_categories)

@main_bp.route('/bestsellers')
def bestsellers():
    collection_sections = []
    return render_template('bestsellers.html', collection_sections=collection_sections)

@main_bp.route('/collections')
def collections():
    return render_template('collections.html')

@main_bp.route('/sale')
def sale():
    return render_template('sale.html')

@main_bp.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    try:
        user = session['user']
        user_id = user.get('id') or user.get('user_id')
        
        print(f"[DEBUG] Account page accessing with user_id: {user_id}")
        
        # Get orders from database
        orders = get_orders(user_id)
        print(f"[DEBUG] Found {len(orders)} orders for user {user_id}")
        
        # Process each order to retrieve or generate items
        for order in orders:
            # Try to get actual order items
            order_items = get_actual_order_items(order['order_id'])
            
            if order_items:
                # We have actual items from order_items tables
                order['items'] = order_items
            else:
                # Generate representative items
                order['items'] = generate_representative_items(order, user_id)
            
            # Add shipping info
            order['shipping_info'] = {
                'method': 'Standard Delivery',
                'address': user.get('address', '123 Sample St., Manila'),
                'status': order.get('status', 'pending').capitalize()
            }
        
        # Get wishlist items
        wishlist_items = get_wishlist()
        
        # Determine which section to show
        section = request.args.get('section', 'dashboard')
        if 'show_orders' in session and session.pop('show_orders', False):
            section = 'orders'
        elif 'showOrdersTab' in request.args:
            section = 'orders'
            
        return render_template('account.html', 
                              user=user,
                              orders=orders,
                              wishlist_items=wishlist_items,
                              active_section=section)
                              
    except Exception as e:
        print(f"Error in account route: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('account.html', 
                              user=session['user'],
                              orders=[],
                              wishlist_items=[],
                              active_section='dashboard')

def get_category_folder(category):
    """Get the correct folder name for a book category"""
    if category == "Fiction":
        return "fiction_images"
    elif category == "Non-Fiction":
        return "non-fiction_images"
    elif category == "Science & Technology":
        return "science-technology_images"
    elif category == "Self-Help":
        return "self-help-book_images"
    return "fiction_images"  

def get_order_items(order_id):
    """Get items for an order from both databases"""
    items = []
    
    # Get items from books.db
    try:
        from database_connection.connector import get_db_connection
        books_conn = get_db_connection('books.db')
        books_cursor = books_conn.cursor()
        
        books_cursor.execute('''
            SELECT oi.product_id, oi.product_name, oi.price, oi.quantity,
                   b.product_image_front, b.category
            FROM order_items oi
            LEFT JOIN books b ON oi.product_id = b.product_id
            WHERE oi.order_id = ?
        ''', (order_id,))
        
        book_items = books_cursor.fetchall()
        books_conn.close()
        
        for item in book_items:
            product_id, name, price, quantity, image, category = item
            folder = get_category_folder(category) if category else "fiction_images"
            
            items.append({
                'product_id': product_id,
                'product_name': name,
                'price': price,
                'quantity': quantity,
                'image_path': f"/static/images/Books_Images/{folder}/{image}.jpg" if image else "/static/images/placeholder.jpg"
            })
    
    except Exception as e:
        print(f"Error getting book items for order {order_id}: {str(e)}")
    
    # Get items from non_books.db
    try:
        non_books_conn = get_db_connection('non_books.db')
        non_books_cursor = non_books_conn.cursor()
        
        non_books_cursor.execute('''
            SELECT oi.product_id, oi.product_name, oi.price, oi.quantity,
                   nb.product_image_front, nb.category
            FROM order_items oi
            LEFT JOIN non_books nb ON oi.product_id = nb.product_id
            WHERE oi.order_id = ?
        ''', (order_id,))
        
        non_book_items = non_books_cursor.fetchall()
        non_books_conn.close()
        
        for item in non_book_items:
            product_id, name, price, quantity, image, category = item
            folder = category.lower().replace(' ', '_') if category else "stationery"
            
            items.append({
                'product_id': product_id,
                'product_name': name,
                'price': price,
                'quantity': quantity,
                'image_path': f"/static/images/Non_Books_Images/{folder}/{image}.jpg" if image else "/static/images/placeholder.jpg"
            })
    
    except Exception as e:
        print(f"Error getting non-book items for order {order_id}: {str(e)}")
    
    return items
    
@main_bp.route('/account/delete-address', methods=['POST'])
def delete_address():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    
    try:
        from utilities.user_management import delete_user_address
        user_id = session['user']['user_id']
        delete_user_address(user_id)
        return redirect(url_for('main.account'))
    except Exception as e:
        print(f"Error deleting address: {str(e)}")
        return redirect(url_for('main.account'))
    
@main_bp.route('/get-user-orders')
def get_user_orders():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user'].get('id')
    orders = get_user_orders(user_id)
    
    return jsonify({'orders': orders})