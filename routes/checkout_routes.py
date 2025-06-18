from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from utilities.checkout import (
    process_checkout, validate_shipping_info,
    get_order_by_id, get_user_orders_from_db, process_billing
)

from utilities.cart import get_cart_items

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

@checkout_bp.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    order = get_order_by_id(order_id)
    
    if not order or order['user_id'] != session['user']['id']:
        return "Order not found", 404
    
    return render_template('order_confirmation.html', order=order)

@checkout_bp.route('/my_orders')
def my_orders():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user_orders = get_user_orders_from_db(session['user']['id'])
    return render_template('my_orders.html', orders=user_orders)

@checkout_bp.route('/order_details/<int:order_id>')
def order_details(order_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    order = get_order_by_id(order_id)
    
    if not order or order['user_id'] != session['user']['id']:
        return "Order not found", 404
    
    return render_template('order_details.html', order=order)

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
        # Handle payment processing here
        payment_method = request.form.get('payment')
        
        # Process the order
        result = process_billing(request.form)
        
        if result['success']:
            return redirect(url_for('checkout.order_confirmation', order_id=result['order_id']))
        else:
            return render_template('billing.html', 
                                 cart_products=cart_products, 
                                 total_amount=total_amount, 
                                 error=result['error'])
    
    return render_template('billing.html', 
                         cart_products=cart_products, 
                         total_amount=total_amount)