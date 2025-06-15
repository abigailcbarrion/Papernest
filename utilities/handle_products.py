from flask import request, jsonify
from utilities.load_items import load_nonbooks, get_nonbook_image_path

def handle_add_non_book_product():
    try:
        # Get form data
        product_name = request.form.get('product_name')
        brand = request.form.get('brand', '')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        quantity = int(request.form.get('stock_quantity', 0))  # Note: your DB uses 'quantity' not 'stock_quantity'
        description = request.form.get('description', '')
        
        # Use your existing database connection
        from database_connection.connector import get_nonbooks_db
        
        with get_nonbooks_db() as conn:
            cursor = conn.cursor()
            
            # Get the next product_id
            cursor.execute('SELECT MAX(product_id) FROM non_books')
            max_id = cursor.fetchone()[0]
            new_id = (max_id or 0) + 1
            
            # Insert new product using your actual database schema
            cursor.execute('''
                INSERT INTO non_books (product_id, product_name, brand, price_php, product_description, quantity, category, product_image_front, product_image_back)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (new_id, product_name, brand, price, description, quantity, category, None, None))
            
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Non-book product added successfully', 'product_id': new_id})
        
    except Exception as e:
        print(f"Error adding non-book product: {e}")
        return jsonify({'success': False, 'message': str(e)})