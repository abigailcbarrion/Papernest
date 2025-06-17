from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from utilities.cart import *
from flask_wtf.csrf import CSRFError

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def cart():
    print("[DEBUG] Cart route accessed")
    
    if 'user' not in session:
        print("[DEBUG] No user in session, redirecting to index")
        return redirect(url_for('main.index'))
    
    print(f"[DEBUG] User in session: {session['user']}")
    
    cart_products, total_amount = get_cart_items()
    print(f"[DEBUG] Cart route - cart_products: {cart_products}")
    print(f"[DEBUG] Cart route - total_amount: {total_amount}")
    
    return render_template('cart.html', cart_products=cart_products, total_amount=total_amount)

@cart_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    print("=== CART ADD ROUTE CALLED ===")
    print(f"User in session: {'user' in session}")
    
    if 'user' not in session:
        print("User not logged in")
        return jsonify({'success': False, 'message': 'Please log in to add items to cart'}), 401
    
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            print("No data provided")
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['product_id', 'product_type', 'product_name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        result = add_to_cart_data(
            data.get('product_id'),
            data.get('product_type'),
            data.get('product_name'),
            data.get('price'),
            data.get('image_path'),
            data.get('quantity', 1)
        )
        
        print(f"Add to cart result: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in add_to_cart route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/cart/update', methods=['POST'])
def update_cart():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in'}), 401
    
    try:
        data = request.get_json()
        result = update_cart_quantity(
            data.get('product_id'),
            data.get('product_type'),
            data.get('quantity')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in'}), 401
    
    try:
        data = request.get_json()
        result = remove_from_cart_data(
            data.get('product_id'),
            data.get('product_type')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/cart/count', methods=['GET'])
def cart_count():
    try:
        count = get_cart_count()
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error getting cart count: {str(e)}")
        return jsonify({'count': 0})

@cart_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in'}), 401
    
    try:
        result = clear_user_cart()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/wishlist/add', methods=['POST'])
def add_to_wishlist():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to add items to wishlist'}), 401
    
    try:
        data = request.get_json()
        result = add_to_wishlist_data(
            data.get('product_id'),
            data.get('product_type')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/wishlist')
def wishlist():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    
    wishlist_items = get_wishlist_items()
    return render_template('wishlist.html', wishlist_items=wishlist_items)