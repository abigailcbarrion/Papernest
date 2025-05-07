from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

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
    # Load books from JSON file
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'books.json')
    
    with open(json_path, 'r') as f:
        books_data = json.load(f)
    
    # Pass the books data to the template
    return render_template('index.html', popular_books=books_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

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

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        session.setdefault('cart', [])
        session.setdefault('wishlist', [])

        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = user
                session.setdefault('cart', [])
                session.setdefault('wishlist', [])
                return redirect(url_for('home'))

        return "Invalid credentials. Try again."
    return render_template('login.html')

@app.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    return render_template('account.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

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
    return redirect(url_for('home'))


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
    return redirect(url_for('home'))


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
