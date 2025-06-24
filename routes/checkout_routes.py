from flask import Blueprint, request, redirect, url_for, session, render_template, flash, jsonify
from utilities.checkout import (
    validate_shipping_info, process_checkout, process_billing_fixed
)
from utilities.order import (
    get_order_by_id, save_order_to_database, 
    process_billing, clear_cart
)
from utilities.checkout import save_order_with_user_id
        
from utilities.cart import get_cart_items
from utilities.user_management import get_user_orders_from_db
import json
from datetime import datetime
import uuid

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user = session['user']
    
    cart_products, total_amount = get_cart_items()

    print(f"[DEBUG] Cart products count: {len(cart_products)}")
    print(f"[DEBUG] Total amount: {total_amount}")
    
    if not cart_products:
        print("[DEBUG] No products in cart, redirecting back to cart")
        flash("Your cart is empty. Please add items before checkout.", "warning")
        return redirect(url_for('cart.cart'))
    
    selected_only = request.args.get('selected') == 'true'
    
    if request.method == 'POST':
        errors = validate_shipping_info(request.form)
        if errors:
            return render_template('checkout.html', cart_products=cart_products, total_amount=total_amount, errors=errors, selected_only=selected_only, user=user)
        
        selected_product_ids = request.form.getlist('selected_products')

        if selected_product_ids:
            cart_products = [p for p in cart_products if str(p['product_id']) in selected_product_ids]

        result = process_checkout(request.form)
        
        if result['success']:
            return redirect(url_for('checkout.order_confirmation', order_id=result['order_id']))
        else:
            return render_template('checkout.html', cart_products=cart_products, total_amount=total_amount, error=result['error'], selected_only=selected_only, user=user)
    
    return render_template('checkout.html', cart_products=cart_products, total_amount=total_amount, selected_only=selected_only, user=user)

# @checkout_bp.route('/order_confirmation/<order_id>')
# def order_confirmation(order_id):
#     if 'user' not in session:
#         return redirect(url_for('auth.login'))
    
#     order = get_order_by_id(order_id)
    
#     user_id = session['user'].get('id') or session['user'].get('user_id')
    
#     if not order or str(order.get('user_id')) != str(user_id):
#         return "Order not found", 404
    
#     return render_template('order_confirmation.html', order=order)

# @checkout_bp.route('/my_orders')
# def my_orders():
#     if 'user' not in session:
#         return redirect(url_for('auth.login'))
    
#     user_orders = get_user_orders_from_db(session['user']['id'])
#     return render_template('my_orders.html', orders=user_orders)

# @checkout_bp.route('/order_details/<order_id>')
# def order_details(order_id):
#     if 'user' not in session:
#         return redirect(url_for('auth.login'))
    
#     order = get_order_by_id(order_id)
    
#     user_id = session['user'].get('id') or session['user'].get('user_id')
#     if not order or str(order.get('user_id')) != str(user_id):
#         print(f"[DEBUG] Order access denied - order user_id: {order.get('user_id')}, session user_id: {user_id}")
#         return "Order not found", 404
    
#     return render_template('order_details.html', order=order)

@checkout_bp.route('/billing', methods=['GET', 'POST'])
def billing():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    # Get cart products and total
    cart_products, total_amount = get_cart_items()
    
    # If cart is empty, redirect back to cart
    if not cart_products:
        return redirect(url_for('cart.cart'))
    
    if request.method == 'POST':
        # Get payment details
        payment_method = request.form.get('payment')
        payment_details = request.form.get('payment_details')
        
        print(f"[DEBUG] Processing billing with payment: {payment_method}")
        
        # Process the order
        result = process_billing(payment_method, payment_details)
        
        if result['success']:
            # Clear cart after successful order
            clear_cart()
            
            # Save order ID in session
            session['last_order_id'] = result['order_id']
            
            # Check localStorage flag in JavaScript
            # The JavaScript will set localStorage.setItem('showOrdersTab', 'true')
            
            # Always redirect to account page after order
            # The section will be handled by client-side JavaScript
            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('main.account'))
        else:
            flash(result['error'], 'error')
            return render_template('billing.html', 
                                cart_products=cart_products, 
                                total_amount=total_amount, 
                                error=result['error'])
    
    return render_template('billing.html', 
                        cart_products=cart_products, 
                        total_amount=total_amount)

@checkout_bp.route('/process-payment', methods=['POST'])
def process_payment():
    """Process payment from either JSON or form submission"""
    try:
        # Check if this is an AJAX/JSON request
        if request.is_json:
            # Handle JSON data (from fetch API)
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No data received'})
                
            payment_method = data.get('payment_method')
            user_id = data.get('user_id')
            username = data.get('username')
            
            print(f"[DEBUG] Processing payment via JSON: method={payment_method}, user_id={user_id}")
            
            # Process with explicit user_id from request
            result = save_order_with_user_id(payment_method, user_id, username)
            
            # Return JSON response
            if result.get('success'):
                return jsonify({
                    'success': True, 
                    'order_id': result.get('order_id')
                })
            else:
                return jsonify({
                    'success': False, 
                    'message': result.get('error', 'Failed to process payment')
                })
                
        else:
            # Handle form submission (traditional form)
            if 'user' not in session:
                return jsonify({'success': False, 'message': 'User not logged in'})
            
            user = session['user']
            user_id = user.get('id')
            
            # Get payment method from form
            payment_method = request.form.get('payment', 'Unknown')
            
            # Optional: Parse payment details if provided
            payment_details = request.form.get('payment_details')
            if payment_details:
                try:
                    payment_info = json.loads(payment_details)
                    payment_method = payment_info.get('method', payment_method)
                except:
                    pass
            
            # Process the order using traditional method
            result = process_billing(payment_method, payment_details)
            
            # Handle the response based on request type
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if result.get('success'):
                    return jsonify({'success': True, 'order_id': result.get('order_id')})
                else:
                    return jsonify({'success': False, 'message': result.get('error', 'Payment failed')})
            else:
                if result.get('success'):
                    # Clear the cart
                    clear_cart()
                    session['last_order_id'] = result.get('order_id')
                    return redirect(url_for('checkout.order_confirmation', order_id=result.get('order_id')))
                else:
                    flash(result.get('error', 'Payment failed'), 'error')
                    return redirect(url_for('checkout.billing'))
    
    except Exception as e:
        print(f"[ERROR] Payment processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error based on request type
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': False, 'message': str(e)})
        else:
            flash(f"An error occurred: {str(e)}", 'error')
            return redirect(url_for('checkout.billing'))
        
@checkout_bp.route('/view-recent-order')
def view_recent_order():
    """Simple redirect to account page with orders section"""
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    flash('Your order has been placed successfully!', 'success')
    
    # Redirect to account page with orders section
    return redirect(url_for('main.account') + '?section=orders')