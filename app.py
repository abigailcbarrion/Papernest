from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
from forms import LoginForm, RegistrationForm
import json
import os
import random

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.secret_key = 'your_secret_key'  # Required for session

# ---------- File Paths ----------
USERS_FILE = 'data/users.json'
BOOKS_FILE = 'data/books.json'

# ---------- Helper Functions ----------
def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_users():
    return load_json(USERS_FILE)

def save_users(users):
    save_json(USERS_FILE, users)

def load_books():
    return load_json(BOOKS_FILE)

# ---------- Routes ----------
@app.route('/')
def index():
    # Load data from JSON files
    json_path = os.path.join(app.root_path, 'data', 'books.json')
    authors_path = os.path.join(app.root_path, 'data', 'featured_authors.json')
    
    with open(json_path, 'r') as f:
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
        with open(authors_path, 'r') as f:
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
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        users = load_users()
        username = form.username.data
        password = form.password.data

        # Check if user already exists
        for user in users:
            if user['username'] == username:
                return "Username already exists. Try another one."

        new_user = {
            "id": len(users) + 1,
            "username": username,
            "password": password
        }
        users.append(new_user)
        save_users(users)
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        users = load_users()
        username = form.username.data
        password = form.password.data
        session.setdefault('cart', [])
        session.setdefault('wishlist', [])

        print(f"Input Username: {username}, Input Password: {password}")  # Debugging
        print(f"Users: {users}")  # Debugging

        # Validate username and password against the JSON file
        for user in users:
            if user['username'] == username:
                if user['password'] == password:
                    # Successful login
                    session['user'] = user
                    session.setdefault('cart', [])
                    session.setdefault('wishlist', [])
                    return redirect(url_for('index'))
                else:
                    # Password mismatch
                    return "Invalid password. Please try again."

        return "Invalid credentials. Try again."
    return render_template('login.html', form=form)

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

# ---------- Main ----------
if __name__ == '__main__':
    app.run(debug=True)
