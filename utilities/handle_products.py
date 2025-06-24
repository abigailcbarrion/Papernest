from database_connection.connector import get_db_connection
import sqlite3
import os
from datetime import datetime

def get_all_products(product_type='all', category=None, page=1, per_page=12, search_term=None, sort_by=None, sort_order='asc'):
    """
    Get products with pagination, filtering, search and sorting
    
    Args:
        product_type: 'books', 'non_books', or 'all'
        category: Filter by category
        page: Page number
        per_page: Items per page
        search_term: Search by name/title/description
        sort_by: Column to sort by
        sort_order: 'asc' or 'desc'
    """
    products = []
    offset = (page - 1) * per_page
    
    try:
        # Handle books if requested
        if product_type in ['all', 'books']:
            conn = get_db_connection('books.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT *, 'book' as product_type FROM books"
            params = []
            
            # Add search conditions
            if search_term:
                query += " WHERE book_name LIKE ? OR author LIKE ? OR product_description LIKE ?"
                params.extend([f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'])
                
            # Add category filter
            if category:
                if 'WHERE' in query:
                    query += " AND category = ?"
                else:
                    query += " WHERE category = ?"
                params.append(category)
                
            # Join with inventory
            query += " LEFT JOIN inventory ON books.product_id = inventory.product_id"
                
            # Add sorting
            if sort_by:
                valid_sort_columns = ['book_name', 'author', 'price_php', 'publication_date', 'stock_quantity']
                if sort_by in valid_sort_columns:
                    query += f" ORDER BY {sort_by} {sort_order.upper()}"
            else:
                query += " ORDER BY book_name ASC"
                
            # Add pagination
            query += " LIMIT ? OFFSET ?"
            params.extend([per_page, offset])
            
            cursor.execute(query, params)
            book_products = [dict(row) for row in cursor.fetchall()]
            
            # Add product image paths
            for product in book_products:
                product['product_image_path'] = f"/static/images/Books_Images/{product.get('product_image_front', '')}"
                product['product_type'] = 'book'
            
            products.extend(book_products)
            conn.close()
            
        # Handle non-books if requested
        if product_type in ['all', 'non_books']:
            conn = get_db_connection('non_books.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT *, 'non_book' as product_type FROM non_books"
            params = []
            
            # Add search conditions
            if search_term:
                query += " WHERE product_name LIKE ? OR product_description LIKE ? OR brand LIKE ?"
                params.extend([f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'])
                
            # Add category filter
            if category:
                if 'WHERE' in query:
                    query += " AND category = ?"
                else:
                    query += " WHERE category = ?"
                params.append(category)
                
            # Join with inventory
            query += " LEFT JOIN inventory ON non_books.product_id = inventory.product_id"
                
            # Add sorting
            if sort_by:
                valid_sort_columns = ['product_name', 'price_php', 'brand', 'stock_quantity']
                if sort_by in valid_sort_columns:
                    query += f" ORDER BY {sort_by} {sort_order.upper()}"
            else:
                query += " ORDER BY product_name ASC"
                
            # Add pagination
            query += " LIMIT ? OFFSET ?"
            params.extend([per_page, offset])
            
            cursor.execute(query, params)
            nonbook_products = [dict(row) for row in cursor.fetchall()]
            
            # Add product image paths
            for product in nonbook_products:
                product['product_image_path'] = f"/static/images/Non_Books_Images/{product.get('product_image_front', '')}"
                product['product_type'] = 'non_book'
            
            products.extend(nonbook_products)
            conn.close()
            
        return products
        
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

def get_product_by_id(product_id, product_type=None):
    """Get a specific product by ID with inventory information"""
    try:
        # Check if product_id is valid
        if not product_id:
            return None
            
        # Try books.db first if product_type is not specified or is 'book'
        if not product_type or product_type == 'book':
            try:
                conn = get_db_connection('books.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT b.*, i.stock_quantity, i.reserved_quantity, 'book' as product_type 
                    FROM books b 
                    LEFT JOIN inventory i ON b.product_id = i.product_id 
                    WHERE b.product_id = ?
                """, (product_id,))
                
                product = cursor.fetchone()
                if product:
                    product = dict(product)
                    product['product_image_path'] = f"/static/images/Books_Images/{product.get('product_image_front', '')}"
                    product['product_type'] = 'book'
                    conn.close()
                    return product
                conn.close()
            except Exception as e:
                print(f"Error checking books.db: {e}")
        
        # Try non_books.db if product_type is not specified or is 'non_book'
        if not product_type or product_type == 'non_book':
            try:
                conn = get_db_connection('non_books.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT nb.*, i.stock_quantity, i.reserved_quantity, 'non_book' as product_type 
                    FROM non_books nb
                    LEFT JOIN inventory i ON nb.product_id = i.product_id
                    WHERE nb.product_id = ?
                """, (product_id,))
                
                product = cursor.fetchone()
                if product:
                    product = dict(product)
                    product['product_image_path'] = f"/static/images/Non_Books_Images/{product.get('product_image_front', '')}"
                    product['product_type'] = 'non_book'
                    conn.close()
                    return product
                conn.close()
            except Exception as e:
                print(f"Error checking non_books.db: {e}")
                
        return None
        
    except Exception as e:
        print(f"Error getting product by ID: {e}")
        return None

def update_product_inventory(product_id, product_type, quantity_change, is_reserved=False):
    """
    Update product inventory
    
    Args:
        product_id: ID of the product
        product_type: 'book' or 'non_book'
        quantity_change: Positive to add stock, negative to reduce
        is_reserved: True to update reserved quantity instead of stock
    """
    try:
        if product_type == 'books' or product_type == 'book':
            db_name = 'books.db'
        elif product_type == 'non_books' or product_type == 'non-books' or product_type == 'non_book' or product_type == 'non-book':
            db_name = 'non_books.db'
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        
        # Check if inventory record exists
        cursor.execute("SELECT * FROM inventory WHERE product_id = ?", (product_id,))
        inventory = cursor.fetchone()
        
        if inventory:
            if is_reserved:
                # Update reserved quantity
                cursor.execute("""
                    UPDATE inventory 
                    SET reserved_quantity = reserved_quantity + ?, 
                        last_updated = datetime('now')
                    WHERE product_id = ?
                """, (quantity_change, product_id))
            else:
                # Update stock quantity
                cursor.execute("""
                    UPDATE inventory 
                    SET stock_quantity = stock_quantity + ?, 
                        last_updated = datetime('now')
                    WHERE product_id = ?
                """, (quantity_change, product_id))
        else:
            # Create new inventory record
            if is_reserved:
                cursor.execute("""
                    INSERT INTO inventory (product_id, stock_quantity, reserved_quantity)
                    VALUES (?, 0, ?)
                """, (product_id, quantity_change))
            else:
                cursor.execute("""
                    INSERT INTO inventory (product_id, stock_quantity, reserved_quantity)
                    VALUES (?, ?, 0)
                """, (product_id, quantity_change))
                
        conn.commit()
        print(f"Inventory updated successfully for product ID {product_id}")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error updating inventory: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def save_order_items(order_id, items):
    """
    Save order items to the appropriate database
    
    Args:
        order_id: ID of the order
        items: List of items in the order
    """
    try:
        books_conn = get_db_connection('books.db')
        non_books_conn = get_db_connection('non_books.db')
        books_cursor = books_conn.cursor()
        non_books_cursor = non_books_conn.cursor()
        
        for item in items:
            product_id = item.get('product_id')
            product_name = item.get('product_name')
            product_type = item.get('product_type')
            price = float(item.get('price', 0))
            quantity = int(item.get('quantity', 1))
            subtotal = price * quantity
            
            # Determine which database to use
            if product_type == 'book':
                cursor = books_cursor
                conn = books_conn
            else:
                cursor = non_books_cursor
                conn = non_books_conn
                
            # Insert the order item
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, product_type, price, quantity, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (order_id, product_id, product_name, product_type, price, quantity, subtotal))
            
            # Update inventory (remove from stock, update reserved)
            update_product_inventory(product_id, product_type, -quantity)
            
        books_conn.commit()
        non_books_conn.commit()
        books_conn.close()
        non_books_conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error saving order items: {e}")
        if books_conn:
            books_conn.rollback()
            books_conn.close()
        if non_books_conn:
            non_books_conn.rollback() 
            non_books_conn.close()
        return False

def get_product_categories(product_type='all'):
    """Get all product categories"""
    categories = []
    
    try:
        if product_type in ['all', 'books']:
            conn = get_db_connection('books.db')
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL")
            book_categories = [row[0] for row in cursor.fetchall()]
            categories.extend(book_categories)
            conn.close()
            
        if product_type in ['all', 'non_books']:
            conn = get_db_connection('non_books.db')
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM non_books WHERE category IS NOT NULL")
            nonbook_categories = [row[0] for row in cursor.fetchall()]
            categories.extend(nonbook_categories)
            conn.close()
            
        return sorted(list(set(categories)))  # Remove duplicates and sort
        
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

def add_product(product_data, product_type):
    """
    Add a new product to the database
    
    Args:
        product_data: Dictionary containing product information
        product_type: 'book' or 'non_book'
    """
    try:
        db_name = 'books.db' if product_type == 'book' else 'non_books.db'
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        
        if product_type == 'book':
            cursor.execute("""
                INSERT INTO books (
                    book_name, author, price_php, product_description, 
                    isbn, publisher, publication_date, product_language,
                    no_of_pages, category, product_image_front, product_image_back
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data.get('book_name'), 
                product_data.get('author'),
                product_data.get('price_php'), 
                product_data.get('product_description'),
                product_data.get('isbn'), 
                product_data.get('publisher'),
                product_data.get('publication_date'), 
                product_data.get('product_language'),
                product_data.get('no_of_pages'), 
                product_data.get('category'),
                product_data.get('product_image_front'), 
                product_data.get('product_image_back')
            ))
        else:
            cursor.execute("""
                INSERT INTO non_books (
                    product_name, price_php, product_description, 
                    brand, quantity, category, 
                    product_image_front, product_image_back
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data.get('product_name'),
                product_data.get('price_php'),
                product_data.get('product_description'),
                product_data.get('brand'),
                product_data.get('quantity'),
                product_data.get('category'),
                product_data.get('product_image_front'),
                product_data.get('product_image_back')
            ))
            
        # Get the ID of the newly inserted product
        product_id = cursor.lastrowid
        
        # Add initial inventory if stock quantity is provided
        if 'stock_quantity' in product_data:
            stock_quantity = int(product_data.get('stock_quantity', 0))
            cursor.execute("""
                INSERT INTO inventory (product_id, stock_quantity, reserved_quantity)
                VALUES (?, ?, 0)
            """, (product_id, stock_quantity))
            
        conn.commit()
        conn.close()
        
        return {'success': True, 'product_id': product_id}
        
    except Exception as e:
        print(f"Error adding product: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return {'success': False, 'error': str(e)}

def update_product(product_id, product_data, product_type):
    """
    Update an existing product
    
    Args:
        product_id: ID of the product to update
        product_data: Dictionary containing updated product information
        product_type: 'book' or 'non_book'
    """
    try:
        db_name = 'books.db' if product_type == 'book' else 'non_books.db'
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        
        if product_type == 'book':
            # Update the book table
            update_fields = []
            update_values = []
            
            for field in ['book_name', 'author', 'price_php', 'product_description', 
                         'isbn', 'publisher', 'publication_date', 'product_language',
                         'no_of_pages', 'category', 'product_image_front', 'product_image_back']:
                if field in product_data:
                    update_fields.append(f"{field} = ?")
                    update_values.append(product_data[field])
                    
            if update_fields:
                query = f"UPDATE books SET {', '.join(update_fields)} WHERE product_id = ?"
                update_values.append(product_id)
                cursor.execute(query, update_values)
        else:
            # Update the non_books table
            update_fields = []
            update_values = []
            
            for field in ['product_name', 'price_php', 'product_description', 
                         'brand', 'quantity', 'category', 
                         'product_image_front', 'product_image_back']:
                if field in product_data:
                    update_fields.append(f"{field} = ?")
                    update_values.append(product_data[field])
                    
            if update_fields:
                query = f"UPDATE non_books SET {', '.join(update_fields)} WHERE product_id = ?"
                update_values.append(product_id)
                cursor.execute(query, update_values)
                
        # Update inventory if stock quantity is provided
        if 'stock_quantity' in product_data:
            # Check if inventory record exists
            cursor.execute("SELECT * FROM inventory WHERE product_id = ?", (product_id,))
            inventory = cursor.fetchone()
            
            if inventory:
                cursor.execute("""
                    UPDATE inventory 
                    SET stock_quantity = ?, last_updated = datetime('now')
                    WHERE product_id = ?
                """, (product_data['stock_quantity'], product_id))
            else:
                cursor.execute("""
                    INSERT INTO inventory (product_id, stock_quantity, reserved_quantity)
                    VALUES (?, ?, 0)
                """, (product_id, product_data['stock_quantity']))
                
        conn.commit()
        conn.close()
        
        return {'success': True}
        
    except Exception as e:
        print(f"Error updating product: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return {'success': False, 'error': str(e)}

def delete_product(product_id, product_type):
    """Delete a product from the database"""
    try:
        db_name = 'books.db' if product_type == 'book' else 'non_books.db'
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        
        # Delete from inventory first (foreign key constraint)
        cursor.execute("DELETE FROM inventory WHERE product_id = ?", (product_id,))
        
        # Delete from main product table
        if product_type == 'book':
            cursor.execute("DELETE FROM books WHERE product_id = ?", (product_id,))
        else:
            cursor.execute("DELETE FROM non_books WHERE product_id = ?", (product_id,))
            
        conn.commit()
        conn.close()
        
        return {'success': True}
        
    except Exception as e:
        print(f"Error deleting product: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return {'success': False, 'error': str(e)}

def get_order_items(order_id):
    """Get all items for a specific order from both databases"""
    all_items = []
    
    try:
        # Get items from books.db
        conn = get_db_connection('books.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT oi.*, b.product_image_front
            FROM order_items oi
            LEFT JOIN books b ON oi.product_id = b.product_id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        book_items = [dict(row) for row in cursor.fetchall()]
        for item in book_items:
            item['image_path'] = f"/static/images/Books_Images/{item.get('product_image_front', '')}"
            
        all_items.extend(book_items)
        conn.close()
        
        # Get items from non_books.db
        conn = get_db_connection('non_books.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT oi.*, nb.product_image_front
            FROM order_items oi
            LEFT JOIN non_books nb ON oi.product_id = nb.product_id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        nonbook_items = [dict(row) for row in cursor.fetchall()]
        for item in nonbook_items:
            item['image_path'] = f"/static/images/Non_Books_Images/{item.get('product_image_front', '')}"
            
        all_items.extend(nonbook_items)
        conn.close()
        
        return all_items
        
    except Exception as e:
        print(f"Error getting order items: {e}")
        return []
    
def get_current_stock(product_id, product_type):
    """Get the current stock quantity of a product"""
    try:
        if product_type == 'books' or product_type == 'book':
            db_name = 'books.db'
        elif product_type == 'non_books' or product_type == 'non-books' or product_type == 'non_book' or product_type == 'non-book':
            db_name = 'non_books.db'
        else:
            return 0
        conn = get_db_connection(db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT stock_quantity FROM inventory WHERE product_id = ?", (product_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]
        return 0
    except Exception as e:
        print(f"Error getting current stock: {e}")
        return 0