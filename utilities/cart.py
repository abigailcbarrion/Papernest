from flask import session, jsonify
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path

def add_to_cart_data(product_id, product_type, product_name, price, image_path, quantity=1):
    """Add product to cart with full data"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}

    if not all([product_id, product_type, product_name, price]):
        return {'success': False, 'message': 'Missing product information'}
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if item already exists in cart
    for item in session['cart']:
        if item['product_id'] == product_id and item['product_type'] == product_type:
            item['quantity'] += quantity
            session.modified = True
            return {'success': True, 'message': 'Cart updated', 'cart_count': get_cart_count()}
    
    # Add new item to cart
    cart_item = {
        'product_id': product_id,
        'product_type': product_type,
        'product_name': product_name,
        'price': float(price),
        'image_path': image_path,
        'quantity': quantity
    }
    
    session['cart'].append(cart_item)
    session.modified = True
    
    return {'success': True, 'message': 'Added to cart', 'cart_count': get_cart_count()}

def update_cart_quantity(product_id, product_type, new_quantity):
    """Update quantity of item in cart"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}
    
    if 'cart' not in session:
        return {'success': False, 'message': 'Cart is empty'}
    
    for item in session['cart']:
        if item['product_id'] == product_id and item['product_type'] == product_type:
            if new_quantity <= 0:
                session['cart'].remove(item)
            else:
                item['quantity'] = new_quantity
            session.modified = True
            return {'success': True, 'message': 'Cart updated'}
    
    return {'success': False, 'message': 'Item not found in cart'}

def remove_from_cart_data(product_id, product_type):
    """Remove specific item from cart"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}
    
    if 'cart' not in session:
        return {'success': False, 'message': 'Cart is empty'}
    
    session['cart'] = [item for item in session['cart'] 
                      if not (item['product_id'] == product_id and item['product_type'] == product_type)]
    
    session.modified = True
    return {'success': True, 'message': 'Item removed from cart'}

def clear_cart():
    """Clear all items from cart"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}
    
    session['cart'] = []
    session.modified = True
    
    return {'success': True, 'message': 'Cart cleared'}

def get_cart_count():
    """Get current cart count (total quantity)"""
    if 'user' not in session:
        return 0
    
    cart = session.get('cart', [])
    return sum(item.get('quantity', 1) for item in cart)

def get_cart_total():
    """Calculate total cart amount"""
    if 'user' not in session:
        return 0.0
    
    cart = session.get('cart', [])
    total = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart)
    return round(total, 2)

def get_cart_items():
    """Get all cart items with product details"""
    if 'user' not in session:
        return [], 0.0
    
    cart = session.get('cart', [])
    total_amount = get_cart_total()
    
    return cart, total_amount

def add_to_wishlist_data(product_id, product_type):
    """Add product to wishlist"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}

    if 'wishlist' not in session:
        session['wishlist'] = []

    wishlist_item = {
        'product_id': product_id,
        'product_type': product_type
    }
    
    # Check if already in wishlist
    for item in session['wishlist']:
        if item['product_id'] == product_id and item['product_type'] == product_type:
            return {'success': False, 'message': 'Already in wishlist'}
    
    session['wishlist'].append(wishlist_item)
    session.modified = True
    return {'success': True, 'message': 'Added to wishlist'}

def remove_from_wishlist_data(product_id, product_type):
    """Remove product from wishlist"""
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}

    if 'wishlist' not in session:
        return {'success': False, 'message': 'Wishlist is empty'}
    
    session['wishlist'] = [item for item in session['wishlist'] 
                          if not (item['product_id'] == product_id and item['product_type'] == product_type)]
    
    session.modified = True
    return {'success': True, 'message': 'Removed from wishlist'}

def get_wishlist_count():
    """Get current wishlist count"""
    if 'user' not in session:
        return 0
    
    return len(session.get('wishlist', []))

def get_wishlist_items():
    """Get all wishlist items with product details"""
    if 'user' not in session:
        return []

    wishlist = session.get('wishlist', [])
    wishlist_items = []
    
    books = load_books()
    nonbooks = load_nonbooks()
    
    for item in wishlist:
        if item['product_type'] == 'book':
            for book in books:
                if book['Product ID'] == item['product_id']:
                    book['image_path'] = get_books_image_path(book['Product ID'])
                    book['product_type'] = 'book'
                    wishlist_items.append(book)
                    break
        elif item['product_type'] == 'non_book':
            for nonbook in nonbooks:
                if nonbook['Product ID'] == item['product_id']:
                    nonbook['image_path'] = get_nonbook_image_path(nonbook['Product ID'])
                    nonbook['product_type'] = 'non_book'
                    wishlist_items.append(nonbook)
                    break
    
    return wishlist_items

def get_cart_and_wishlist_counts():
    """Get both cart and wishlist counts for template context"""
    return {
        'cart_count': get_cart_count(),
        'wishlist_count': get_wishlist_count()
    }

# Legacy compatibility functions
def add_to_cart(product_id):
    """Legacy function - redirects to new function"""
    return {'success': False, 'message': 'Use add_to_cart_data instead'}

def remove_from_cart(product_id):
    """Legacy function - redirects to new function"""
    return {'success': False, 'message': 'Use remove_from_cart_data instead'}

def add_to_wishlist(book_id):
    """Legacy function - redirects to new function"""
    return {'success': False, 'message': 'Use add_to_wishlist_data instead'}

def remove_from_wishlist(book_id):
    """Legacy function - redirects to new function"""
    return {'success': False, 'message': 'Use remove_from_wishlist_data instead'}