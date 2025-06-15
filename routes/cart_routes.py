from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from utilities.cart import (
    add_to_cart_data,
    update_cart_quantity,
    remove_from_cart_data,
    clear_cart,
    get_cart_count,
    get_cart_total,
    get_cart_items,
    add_to_wishlist_data,
    remove_from_wishlist_data,
    get_wishlist_count,
    get_wishlist_items
)

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def cart():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    
    cart_products, total_amount = get_cart_items()
    
    return render_template('cart.html', 
                        cart_products=cart_products, 
                        total_amount=total_amount)

@cart_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to add items to cart'})
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        
        product_id = data.get('product_id')
        product_type = data.get('product_type')
        product_name = data.get('product_name')
        price = data.get('price')
        image_path = data.get('image_path')
        quantity = data.get('quantity', 1)
        
        result = add_to_cart_data(product_id, product_type, product_name, price, image_path, quantity)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({'success': False, 'message': 'Error adding product to cart'})

@cart_bp.route('/cart/update', methods=['POST'])
def update_cart():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in'})
    
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        product_type = data.get('product_type')
        quantity = data.get('quantity')
        
        result = update_cart_quantity(product_id, product_type, quantity)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error updating cart: {e}")
        return jsonify({'success': False, 'message': str(e)})

@cart_bp.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in'})
    
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        product_type = data.get('product_type')
        
        result = remove_from_cart_data(product_id, product_type)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error removing from cart: {e}")
        return jsonify({'success': False, 'message': str(e)})

@cart_bp.route('/cart/clear', methods=['POST'])
def clear_cart_route():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in'})
    
    try:
        result = clear_cart()
        return jsonify(result)
        
    except Exception as e:
        print(f"Error clearing cart: {e}")
        return jsonify({'success': False, 'message': str(e)})

@cart_bp.route('/cart/count', methods=['GET'])
def cart_count():
    try:
        count = get_cart_count()
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error getting cart count: {e}")
        return jsonify({'count': 0})

@cart_bp.route('/wishlist/add', methods=['POST'])
def add_to_wishlist():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to add items to wishlist'})
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        
        product_id = data.get('product_id')
        product_type = data.get('product_type')
        
        result = add_to_wishlist_data(product_id, product_type)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error adding to wishlist: {e}")
        return jsonify({'success': False, 'message': 'Error adding product to wishlist'})

@cart_bp.route('/wishlist/remove', methods=['POST'])
def remove_from_wishlist():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in'})
    
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        product_type = data.get('product_type')
        
        result = remove_from_wishlist_data(product_id, product_type)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error removing from wishlist: {e}")
        return jsonify({'success': False, 'message': str(e)})

@cart_bp.route('/wishlist/count', methods=['GET'])
def wishlist_count():
    try:
        count = get_wishlist_count()
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error getting wishlist count: {e}")
        return jsonify({'count': 0})

@cart_bp.route('/wishlist')
def wishlist():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    
    wishlist_items = get_wishlist_items()
    
    return render_template('wishlist.html', wishlist_items=wishlist_items)