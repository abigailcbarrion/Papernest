from flask import session, jsonify
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path

def add_to_cart(product_id):
    """Add product to cart"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}

    if not product_id:
        return {'success': False, 'message': 'Product ID required'}
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Add product to cart (allow duplicates for quantity)
    session['cart'].append(product_id)
    session.modified = True
    
    return {'success': True, 'message': 'Added to cart', 'cart_count': len(session['cart'])}

def remove_from_cart(product_id):
    """Remove one instance of product from cart"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}

    if 'cart' in session and product_id in session['cart']:
        session['cart'].remove(product_id)
        session.modified = True
        return {'success': True, 'message': 'Removed from cart'}
    
    return {'success': False, 'message': 'Product not in cart'}

def update_cart_item(product_id, action):
    """Update cart quantity via AJAX"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}
    
    if 'cart' not in session:
        session['cart'] = []
    
    if action == 'add':
        session['cart'].append(product_id)
    elif action == 'remove' and product_id in session['cart']:
        session['cart'].remove(product_id)
    elif action == 'delete':
        session['cart'] = [item for item in session['cart'] if item != product_id]
    
    session.modified = True
    
    # Get updated cart info
    from utilities.checkout import get_cart_products
    cart_products, total_amount = get_cart_products()
    
    return {
        'success': True,
        'cart_count': len(session['cart']),
        'total_amount': total_amount,
        'message': 'Cart updated'
    }

def clear_cart():
    """Clear all items from cart"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}
    
    session['cart'] = []
    session.modified = True
    
    return {'success': True, 'message': 'Cart cleared'}

def get_cart_count():
    """Get current cart count"""
    return len(session.get('cart', []))

def get_cart_items():
    """Get all cart items with product details"""
    from utilities.checkout import get_cart_products
    return get_cart_products()

def add_to_wishlist(book_id):
    """Add book to wishlist"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}

    if 'wishlist' not in session:
        session['wishlist'] = []

    if book_id not in session['wishlist']:  
        session['wishlist'].append(book_id)
        session.modified = True
        return {'success': True, 'message': 'Added to wishlist'}
    
    return {'success': False, 'message': 'Already in wishlist'}

def remove_from_wishlist(book_id):
    """Remove book from wishlist"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}

    if 'wishlist' in session and book_id in session['wishlist']:
        session['wishlist'].remove(book_id)
        session.modified = True
        return {'success': True, 'message': 'Removed from wishlist'}
    
    return {'success': False, 'message': 'Not in wishlist'}

def get_wishlist_items():
    """Get all wishlist items with product details"""
    if 'user' not in session:
        return []

    books = load_books()
    wishlist_books = [book for book in books if book['Product ID'] in session.get('wishlist', [])]
    
    # Add image paths
    for book in wishlist_books:
        book['image_path'] = get_books_image_path(book['Product ID'])
    
    return wishlist_books

def get_wishlist_count():
    """Get current wishlist count"""
    return len(session.get('wishlist', []))

def get_cart_and_wishlist_counts():
    """Get both cart and wishlist counts for template context"""
    return {
        'cart_count': get_cart_count(),
        'wishlist_count': get_wishlist_count()
    }