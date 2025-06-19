from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from utilities.cart import *
from flask_wtf.csrf import CSRFError
from utilities.session_utils import get_current_user_id

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
    
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to add items to cart'}), 401
    
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Only validate fields we actually need
        required_fields = ['product_id', 'product_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # IMPORTANT: Only pass the parameters the function expects
        result = add_to_cart_data(
            data.get('product_id'),
            data.get('product_type', 'books'),
            int(data.get('quantity', 1))
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
def add_wishlist():
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
        print(f"Error in add_wishlist route: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/wishlist/remove', methods=['POST'])
def remove_wishlist():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to remove items from wishlist'}), 401
    
    try:
        data = request.get_json()
        result = remove_from_wishlist_data(
            data.get('product_id'),
            data.get('product_type')
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error in remove_wishlist route: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/wishlist')
def wishlist():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    
    wishlist_items = get_wishlist_items()
    return render_template('wishlist.html', wishlist_items=wishlist_items)

@cart_bp.route('/wishlist/check', methods=['POST'])
def check_wishlist():
    if 'user' not in session:
        return jsonify({'in_wishlist': False})
    
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        product_type = data.get('product_type')

        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'in_wishlist': False})
        
        conn = get_users_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM wishlist
            WHERE user_id = ? AND product_id = ? AND product_type = ?""",
            (user_id, str(product_id), product_type))

        result = cursor.fetchone()
        cursor.close()

        return jsonify({'in_wishlist': result[0] > 0})

    except Exception as e:
        print(f"Error checking wishlist: {str(e)}")
        return jsonify({'in_wishlist': False})