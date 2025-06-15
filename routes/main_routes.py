from flask import Blueprint, render_template, session, redirect, url_for
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
    from flask import session, redirect, url_for, render_template
    from utilities.checkout import get_user_orders_from_db
    
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user = session['user']
    recent_orders = get_user_orders_from_db(user['user_id'])[:5]
    return render_template('account.html', user=user, recent_orders=recent_orders)


@main_bp.route('account/wishlist')
def wishlist():
    if 'user' not in session:
        return redirect(url_for('main.index'))

    user = session.get('user')
    return render_template('account.html', user=user, page='wishlist', active_session='wishlist')
