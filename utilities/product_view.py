from flask import render_template, request
import os
import json

BOOKS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'books.json')

def load_books():
    with open(BOOKS_FILE, 'r') as f:
        return json.load(f)

def get_product_view():
    # For now, just show the first book as an example
    books = load_books()
    product = books[0] if books else {}
    return render_template('product_view.html', product=product)