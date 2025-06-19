def get_actual_order_items(order_id):
    """Get actual items for an order from order_items tables"""
    items = []
    
    # 1. Try books database
    try:
        from database_connection.connector import get_db_connection
        conn = get_db_connection('books.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT oi.product_id, oi.product_name, oi.price, oi.quantity
            FROM order_items oi
            WHERE oi.order_id = ?
        """, (order_id,))
        
        for row in cursor.fetchall():
            product_id, name, price, quantity = row
            
            # Use load_items.py function to get the correct image path
            from utilities.load_items import get_books_image_path
            image_path = get_books_image_path(product_id)
            
            items.append({
                'product_id': product_id,
                'product_name': name,
                'price': float(price),
                'quantity': quantity,
                'image_path': image_path
            })
        
        conn.close()
    except Exception as e:
        print(f"Error getting book items: {str(e)}")
    
    # 2. Try non-books database
    try:
        conn = get_db_connection('non_books.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT oi.product_id, oi.product_name, oi.price, oi.quantity
            FROM order_items oi
            WHERE oi.order_id = ?
        """, (order_id,))
        
        for row in cursor.fetchall():
            product_id, name, price, quantity = row
            
            # Use load_items.py function to get the correct image path
            from utilities.load_items import get_nonbook_image_path
            image_path = get_nonbook_image_path(product_id)
            
            items.append({
                'product_id': product_id,
                'product_name': name,
                'price': float(price),
                'quantity': quantity,
                'image_path': image_path
            })
        
        conn.close()
    except Exception as e:
        print(f"Error getting non-book items: {str(e)}")
    
    return items

def generate_representative_items(order, user_id):
    """Generate representative items for an order with no items"""
    from utilities.load_items import load_books, get_books_image_path
    import random
    
    # Get parameters from order
    order_id = order['order_id']
    order_total = float(order.get('total_amount') or 0)
    
    # Try to use items from wishlist first
    from utilities.cart import get_wishlist_items
    wishlist_items = get_wishlist_items()
    
    # Load books as fallback
    all_books = load_books()
    book_map = {str(book['Product ID']): book for book in all_books}
    
    # Items we'll use for this order
    generated_items = []
    remaining_total = order_total
    
    # First try wishlist items
    for wish_item in wishlist_items:
        product_id = wish_item.get('product_id')
        product_type = wish_item.get('product_type', 'book')
        
        if product_type.lower() == 'book' and product_id in book_map:
            book = book_map[product_id]
            price = float(book['Price (PHP)'])
            
            if price > 0 and remaining_total > 0:
                # Calculate reasonable quantity
                quantity = min(3, max(1, int(remaining_total / price)))
                remaining_total -= price * quantity
                
                # Use the utility function to get image path
                image_path = get_books_image_path(product_id)
                
                # Add item to order
                generated_items.append({
                    'product_id': product_id,
                    'product_name': book['Book Name'],
                    'price': price,
                    'quantity': quantity,
                    'image_path': image_path
                })
                
                # If we've accounted for most of the total, stop
                if remaining_total < 100:
                    break
    
    # If we need more items, use random popular books
    if remaining_total > 100 and all_books:
        # Sort by price (descending) as a proxy for popularity
        sorted_books = sorted(all_books, 
                            key=lambda x: float(x['Price (PHP)']), 
                            reverse=True)
        
        # Choose up to 3 random books from the top 10
        available_books = sorted_books[:10]
        random.shuffle(available_books)
        
        for book in available_books[:3]:
            product_id = str(book['Product ID'])
            
            # Skip if already used
            if any(item['product_id'] == product_id for item in generated_items):
                continue
                
            price = float(book['Price (PHP)'])
            
            if price > 0 and remaining_total > 0:
                # Calculate reasonable quantity
                quantity = min(3, max(1, int(remaining_total / price)))
                remaining_total -= price * quantity
                
                # Use the utility function to get image path
                image_path = get_books_image_path(product_id)
                
                # Add item to order
                generated_items.append({
                    'product_id': product_id,
                    'product_name': book['Book Name'],
                    'price': price,
                    'quantity': quantity,
                    'image_path': image_path
                })
                
                # If we've accounted for most of the total, stop
                if remaining_total < 100:
                    break
    
    # If we still have no items, create a placeholder
    if not generated_items:
        generated_items = [{
            'product_id': str(order_id),
            'product_name': f'Books Order #{order_id}',
            'price': order_total,
            'quantity': 1,
            'image_path': '/static/images/placeholder.jpg'
        }]
    
    return generated_items