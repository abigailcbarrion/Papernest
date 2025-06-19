from flask import Blueprint, render_template, session, redirect, url_for, request
from utilities.load_items import get_books_image_path, get_trending, get_nonbook_image_path
from utilities.storage import get_featured_author

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/homepage')
def index():
    featured_author = get_featured_author()
    trending_books = get_trending(curr_section='homepage')
    for item in trending_books:
        item['image_path'] = get_books_image_path(item['Product ID'])
    
    return render_template('index.html', 
                        popular_items=trending_books,
                        featured_author=featured_author, 
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
    return render_template('books.html', popular_items=trending_books, page_type='books')

@main_bp.route('/non_books')
def non_books():
    trending_non_books = get_trending(curr_section='non_books')
    for item in trending_non_books:
        item['image_path'] = get_nonbook_image_path(item['Product ID'])
    return render_template('non_books.html', popular_items=trending_non_books, page_type='non_books')

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
        return redirect(url_for('main.index'))
    
    try:
        from utilities.checkout import get_user_orders_from_db
        from utilities.cart import get_wishlist_items
        
        user = session['user']
        
        # Get recent orders safely
        try:
            recent_orders = get_user_orders_from_db(user['user_id'])[:5]
        except Exception as e:
            print(f"Error getting orders: {str(e)}")
            recent_orders = []
        
        # Get wishlist items safely
        try:
            wishlist_items = get_wishlist_items()
        except Exception as e:
            print(f"Error getting wishlist items: {str(e)}")
            wishlist_items = []
        
        return render_template('account.html', 
                            user=user, 
                            recent_orders=recent_orders,
                            wishlist_items=wishlist_items)
    
    except Exception as e:
        print(f"Error in account route: {str(e)}")
        # Return basic account page if there are errors
        user = session['user']
        return render_template('account.html', 
                            user=user, 
                            recent_orders=[],
                            wishlist_items=[])

@main_bp.route('/account/wishlist')
def wishlist():
    if 'user' not in session:
        return redirect(url_for('main.index'))

    # Redirect to account page with wishlist hash
    return redirect(url_for('main.account') + '#wishlist')

# Fix these route functions - they need to be properly decorated
@main_bp.route('/account/update-address', methods=['POST'])
def update_address():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    
    try:
        from utilities.user_management import update_user_address
        user_id = session['user']['user_id']
        update_user_address(user_id, request.form)
        return redirect(url_for('main.account'))
    except Exception as e:
        print(f"Error updating address: {str(e)}")
        return redirect(url_for('main.account'))

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