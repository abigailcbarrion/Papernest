from flask import Flask, render_template, request, redirect, url_for, session
from forms import LoginForm, RegistrationForm
from utilities.register import handle_register, get_cities_json, get_barangays_json, get_postal_code_json
from utilities.login import handle_login, load_users_from_db  # Changed from load_users
from utilities.load_items import (
    get_nonbook_image_path, get_books_image_path, get_trending,
    load_books, load_nonbooks, get_nonbook_by_id
)
from utilities.storage import get_featured_author
import os

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.secret_key = '631539ff18360356'  

BOOK_CATEGORIES = ['fiction', 'non-fiction', 'science-and-technology', 'self-help-and-personal-development', 'children\'s-books', 'academic-reference-development']
NON_BOOK_CATEGORIES = ["art-supplies", "calendars-and-planners", "notebooks-and-journals", "novelties", "reading-accessories", "supplies"]

def extract_primary_category(category):
    if ' - ' in category:
        return category.split(' - ')[0]
    return category

def get_default_author():
    return {
        "name": "Featured Author",
        "bio": "Information about this author will be coming soon.",
        "image_url": url_for('static', filename='images/placeholder.jpg'),
        "source_url": "#",
        "more_link": "#"
    }

# ---------- Routes ----------
@app.route('/')
@app.route('/homepage')
def index():
    # Load featured author from database
    featured_author = get_featured_author() or get_default_author()
    
    # Loading trending items
    trending_books = get_trending(curr_section='homepage')
    for item in trending_books:
        item['image_path'] = get_books_image_path(item['Product ID'])
    
    return render_template('index.html', 
                        popular_items=trending_books,
                        featured_author=featured_author, 
                        page_type='homepage')


@app.route('/register', methods=['GET', 'POST'])
def register():
    return handle_register()

@app.route('/login', methods=['GET', 'POST'])
def login():
    return handle_login()

@app.route('/admin_dashboard')
def admin_dashboard():
    # Load data to calculate totals
    books = load_books()
    non_books = load_nonbooks()
    users_data = load_users_from_db()
    
    # Calculate totals
    total_products = len(books) + len(non_books)
    total_users = len(users_data)
    
    return render_template('components/admin_dashboard.html', 
                        total_products=total_products,
                        total_users=total_users)

@app.route('/admin_orders', methods=['GET', 'POST'])
def admin_orders():
    return render_template('components/admin_orders.html')

@app.route('/admin_products')
@app.route('/admin_products/<product_type>')
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

@app.route('/admin_products2', methods=['GET', 'POST'])
def admin_products2():
    return render_template('components/admin_products2.html')

@app.route('/admin_registeredUsers', methods=['GET', 'POST'])
def admin_registeredUsers():
    users_data = load_users_from_db()
    
    return render_template('components/admin_registeredUsers.html', users=users_data)

@app.route('/get_cities/<province_code>', methods=['GET'])
def get_cities(province_code):
    return get_cities_json(province_code) 

@app.route('/get_barangays/<city_code>', methods=['GET'])
def get_barangays(city_code):
    return get_barangays_json(city_code)

@app.route('/get_postal_code', methods=['GET'])
def get_postal_code():
    return get_postal_code_json()

@app.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    return render_template('account.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return redirect(url_for('login'))

    book_id = int(request.form['book_id'])
    
    # Ensure session['cart'] exists
    if 'cart' not in session:
        session['cart'] = []
    
    if book_id not in session['cart']:  # Avoid duplicates
        session['cart'].append(book_id)

    session.modified = True  # Update session
    return redirect(url_for('index'))


@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    if 'user' not in session:
        return redirect(url_for('login'))

    book_id = int(request.form['book_id'])

    # Ensure session['wishlist'] exists
    if 'wishlist' not in session:
        session['wishlist'] = []

    if book_id not in session['wishlist']:  # Avoid duplicates
        session['wishlist'].append(book_id)

    session.modified = True  # Update session
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    books = load_books()
    cart_books = [book for book in books if book['Product ID'] in session.get('cart', [])]
    return render_template('cart.html', cart_books=cart_books)

@app.route('/wishlist')
def wishlist():
    if 'user' not in session:
        return redirect(url_for('login'))

    books = load_books()
    wishlist_books = [book for book in books if book['Product ID'] in session.get('wishlist', [])]
    return render_template('wishlist.html', wishlist_books=wishlist_books)

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'cart' in session and book_id in session['cart']:
        session['cart'].remove(book_id)

    return redirect(url_for('cart'))

@app.route('/remove_from_wishlist/<int:book_id>')
def remove_from_wishlist(book_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'wishlist' in session and book_id in session['wishlist']:
        session['wishlist'].remove(book_id)

    return redirect(url_for('wishlist'))

@app.route('/about')
def about():
    # Add logic to load collections
    return render_template('about_us.html')

@app.route('/help')
def help():
    # Add logic to load sale items
    return render_template('faqs.html')

@app.route('/books')
def books():
    trending_books = get_trending(curr_section='books')

    # getting the trending books images
    for item in trending_books:
        item['image_path'] = get_books_image_path(item['Product ID'])
    return render_template('books.html', popular_items=trending_books, page_type='books')

@app.route('/non_books')
def non_books():
    trending_non_books = get_trending(curr_section='non_books')

    # getting trending non-books images
    for item in trending_non_books:
        item['image_path'] = get_nonbook_image_path(item['Product ID'])
    return render_template('non_books.html', popular_items=trending_non_books, page_type='non_books')

@app.route('/bestsellers')
def bestsellers():
    # Load any data you need for the template
    collection_sections = []  # Fill this with your data
    return render_template('bestsellers.html', collection_sections=collection_sections)

@app.route('/collections')
def collections():
    # Add logic to load collections
    return render_template('collections.html')


@app.route('/sale')
def sale():
    # Add logic to load sale items
    return render_template('sale.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # Add logic to load sale items
    return render_template('adminlogin.html')

@app.route('/product/<int:product_id>')
def product_view(product_id):
    books = load_books()
    non_books = load_nonbooks()
    
    # First, try to find the product in books
    product = next((b for b in books if b.get('Product ID') == product_id), None)
    
    if product:
        # It's a book
        product['image_path'] = get_books_image_path(product_id)
        product['back_image_path'] = get_books_image_path(product_id, image_key='Product Image Back')
        similar_products = get_trending(curr_section='books')
        for item in similar_products:
            item['image_path'] = get_books_image_path(item['Product ID'])
        return render_template('product_view.html', product=product, popular_items=similar_products, page_type='books')
    
    # If not found in books, try non-books
    product = next((nb for nb in non_books if nb.get('Product ID') == product_id), None)
    
    if product:
        # It's a non-book
        product['image_path'] = get_nonbook_image_path(product_id)
        product['back_image_path'] = get_nonbook_image_path(product_id, image_key='Product Image Back')
        similar_products = get_trending(curr_section='non_books')
        for item in similar_products:
            item['image_path'] = get_nonbook_image_path(item['Product ID'])
        return render_template('product_view.html', product=product, popular_items=similar_products, page_type='non_books')
    # Product not found in either collection
    return "Product not found", 404

@app.route('/category/<category_name>')
def category_products(category_name):
    books = load_books()
    non_books = load_nonbooks()

    # Map URL category names to actual category names
    category_mapping = {
        "art-supplies": "Art Supplies",
        "calendars-and-planners": "Calendars and Planners",
        "notebooks-and-journals": "Notebooks & Journals", 
        "novelties": "Novelties",
        "reading-accessories": "Reading Accessories",
        "supplies": "Supplies"
    }

    # Get the actual category name from the URL
    actual_category = category_mapping.get(category_name.lower(), category_name)

    # Filter books by category (case-insensitive match)
    filtered_books = [book for book in books if book.get("Category", "").lower().replace(" ", "-") == category_name.lower()]
    # Attach image path
    for book in filtered_books: 
        book['image_path'] = get_books_image_path(book['Product ID'])

    # Filter non-books by primary category
    filtered_non_books = []
    for non_book in non_books:
        category = non_book.get("Category", "")
        primary_category = extract_primary_category(category)
        
        if primary_category == actual_category:
            filtered_non_books.append(non_book)

    for non_book in filtered_non_books:
        non_book['image_path'] = get_nonbook_image_path(non_book['Product ID'])

    if category_name.lower() in NON_BOOK_CATEGORIES:
        page_type = 'non_books'
    else:   
        page_type = 'books'

    all_products = filtered_books + filtered_non_books
    return render_template('components/product_list.html', category=category_name, products=all_products, non_book_categories=NON_BOOK_CATEGORIES, book_categories=BOOK_CATEGORIES, page_type=page_type)

@app.context_processor
def inject_common_variables():
    # Load featured author from database
    featured_author = get_featured_author() or get_default_author()
    return {'featured_author': featured_author}

@app.context_processor
def inject_forms():
    return {
        'login_form': LoginForm(),
        'registration_form': RegistrationForm()
    }

# ---------- Main ----------
if __name__ == '__main__':
    app.run(debug=True)