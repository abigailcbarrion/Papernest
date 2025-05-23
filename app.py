from flask import Flask, render_template, request, redirect, url_for, session
from forms import LoginForm, RegistrationForm
from utilities.register import handle_register, get_cities_json, get_barangays_json, get_postal_code_json
from utilities.login import handle_login
from utilities.product_view import get_product_view
import json
import os

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.secret_key = '631539ff18360356'  

# ---------- File Paths ----------
USERS_FILE = 'data/users.json'
BOOKS_FILE = 'data/books.json'

# ---------- Helper Functions ----------
def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def load_users():
    return load_json(USERS_FILE)

def save_users(users):
    save_json(USERS_FILE, users)

def load_books():
    return load_json(BOOKS_FILE)

# ---------- Routes ----------
@app.route('/')
@app.route('/homepage')
def index():
    # Load data from JSON files
    json_path = os.path.join(app.root_path, 'data', 'books.json')
    authors_path = os.path.join(app.root_path, 'data', 'featured_authors.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        books_data = json.load(f)
    
    # Create a default author as fallback
    default_author = {
        "name": "Featured Author", 
        "bio": "Information about this author will be coming soon.",
        "image_url": url_for('static', filename='images/placeholder.jpg'),
        "source_url": "#",
        "more_link": "#"
    }
    
    try:
        with open(authors_path, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)
        
        # Access the nested "featured_authors" key
        if "featured_authors" in authors_data and authors_data["featured_authors"]:
            # Get the first author from the list
            featured_author = authors_data["featured_authors"][0]
        else:
            featured_author = default_author
            
    except Exception as e:
        print(f"Error loading authors: {str(e)}")
        featured_author = default_author
    
    return render_template('index.html', 
                          popular_books=books_data,
                          featured_author=featured_author)


@app.route('/register', methods=['GET', 'POST'])
def register():
    return handle_register()

@app.route('/login', methods=['GET', 'POST'])
def login():
    return handle_login()

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
    cart_books = [book for book in books if book['id'] in session.get('cart', [])]
    return render_template('cart.html', cart_books=cart_books)

@app.route('/wishlist')
def wishlist():
    if 'user' not in session:
        return redirect(url_for('login'))

    books = load_books()
    wishlist_books = [book for book in books if book['id'] in session.get('wishlist', [])]
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

@app.route('/books')
def books():
    books = load_books()
    return render_template('books.html', books=books)

@app.route('/non_books')
def non_books():
    # Add logic to load non-book items
    return render_template('non_books.html')

@app.route('/bestsellers_and_new_releases')
def bestsellers_and_new_releases():
    # Add logic to load bestsellers
    return render_template('bestsellers_and_new_releases.html')

@app.route('/collections')
def collections():
    # Add logic to load collections
    return render_template('collections.html')

@app.route('/sale')
def sale():
    # Add logic to load sale items
    return render_template('sale.html')

@app.route('/product_view')
def product_view():
    return get_product_view()

@app.context_processor
def inject_forms():
    return {
        'login_form': LoginForm(),
        'registration_form': RegistrationForm()
    }

# ---------- Main ----------
if __name__ == '__main__':
    app.run(debug=True)
