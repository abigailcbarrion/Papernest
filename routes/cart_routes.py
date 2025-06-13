from flask import Blueprint, request, redirect, url_for, session, jsonify, render_template
from utilities.cart import (
    add_to_cart, remove_from_cart, update_cart_item, clear_cart,
    add_to_wishlist, remove_from_wishlist, get_wishlist_items
)

from utilities.checkout import get_cart_products

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart_route():
    product_id = request.form.get('product_id')
    result = add_to_cart(product_id)
    return jsonify(result)

@cart_bp.route('/cart')
def cart():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    cart_products, total_amount = get_cart_products()
    return render_template('cart.html', cart_products=cart_products, total_amount=total_amount)

@cart_bp.route('/remove_from_cart/<product_id>')
def remove_from_cart_route(product_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    remove_from_cart(product_id)
    return redirect(url_for('cart.cart'))

@cart_bp.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = request.json.get('product_id')
    action = request.json.get('action')
    result = update_cart_item(product_id, action)
    return jsonify(result)

@cart_bp.route('/clear_cart')
def clear_cart_route():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    clear_cart()
    return redirect(url_for('cart.cart'))

@cart_bp.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist_route():
    book_id = int(request.form['book_id'])
    result = add_to_wishlist(book_id)
    return redirect(url_for('main.index'))

@cart_bp.route('/wishlist')
def wishlist():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    wishlist_books = get_wishlist_items()
    return render_template('wishlist.html', wishlist_books=wishlist_books)

@cart_bp.route('/remove_from_wishlist/<int:book_id>')
def remove_from_wishlist_route(book_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    remove_from_wishlist(book_id)
    return redirect(url_for('cart.wishlist'))