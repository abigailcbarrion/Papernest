import os
import sqlite3
from flask import url_for, current_app
from database_connection.connector import get_books_db, get_nonbooks_db
import random

NON_BOOK_CATEGORY_FOLDER_MAP = {
    # Art Supplies
    "Art Supplies - Drawing": "art-supplies_images",
    "Art Supplies - Painting": "art-supplies_images",
    "Art Supplies - Supports": "art-supplies_images",
    # Calendars and Planners
    "Calendars and Planners - Calendars": "calendar-planner_images",
    "Calendars and Planners - Planner": "calendar-planner_images",
    # Notebooks & Journals
    "Notebooks & Journals - Binders & Refills": "notebooks-journal_images",
    "Notebooks & Journals - Guided Journals": "notebooks-journal_images",
    "Notebooks & Journals - Notebooks": "notebooks-journal_images",
    # Novelties
    "Novelties - Postcards": "novelties_images",
    "Novelties - Posters": "novelties_images",
    "Novelties - Stickers": "novelties_images",
    # Reading Accessories
    "Reading Accessories - Book Lights": "Reading_accessories_images",
    "Reading Accessories - Bookmarks": "Reading_accessories_images",
    # Supplies
    "Supplies - Filing & Storage": "supplies_images",
    "Supplies - Paper": "supplies_images",
    "Supplies - Writing Instruments": "supplies_images"
}

BOOK_CATEGORY_FOLDER_MAP = {
    "Fiction": "fiction_images",
    "Non-fiction": "non-fiction_images",
    "Children's Books": "childrens-book_images",
    "Science and Technology": "science-technology_images",
    "Academic and Reference Development": "academics-book_images",
    "Self-Help and Personal Development": "self-help-book_images"
}

def load_books():
    # get books from database
    try:
        with get_books_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        
        books = []
        for row in rows:
            book = {
                'Product ID': row['product_id'],
                'Book Name': row['book_name'],
                'Author': row['author'],
                'Price (PHP)': row['price_php'],
                'Product Description': row['product_description'],
                'ISBN': row['isbn'],                           
                'Publisher': row['publisher'],                 
                'Publication Date': row['publication_date'],   
                'Product Language': row['product_language'],   
                'Pages': row['no_of_pages'],           
                'Category': row['category'],
                'Product Image Front': row['product_image_front'],
                'Product Image Back': row['product_image_back']
            }
            books.append(book)
        
        conn.close()
        return books
    except:
        return []

def load_nonbooks():
    """Load all non-books from database"""
    try:
        with get_nonbooks_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM non_books")
        rows = cursor.fetchall()
        
        nonbooks = []
        for row in rows:
            item = {
                'Product ID': row['product_id'],
                'Product Name': row['product_name'],
                'Brand': row['brand'],
                'Price (PHP)': row['price_php'],
                'Product Description': row['product_description'],
                'Quantity': row['quantity'],
                'Category': row['category'],
                'Product Image Front': row['product_image_front'],
                'Product Image Back': row['product_image_back']
            }
            nonbooks.append(item)
        
        conn.close()
        return nonbooks
    except:
        return []

def get_nonbook_by_id(product_id):
    """Get specific non-book by Product ID"""
    try:
        db_path = os.path.join(current_app.root_path, 'data', 'non_books.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM non_books WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        
        if row:
            item = {
                'Product ID': row['product_id'],
                'Product Name': row['product_name'],
                'Brand': row['brand'],
                'Price (PHP)': row['price_php'],
                'Product Description': row['product_description'],
                'Quantity': row['quantity'],
                'Category': row['category'],
                'Product Image Front': row['product_image_front'],
                'Product Image Back': row['product_image_back']
            }
            conn.close()
            return item
        
        conn.close()
        return None
    except:
        return None

def get_nonbooks_by_category(category):
    """Get non-books by category"""
    try:
        with get_nonbooks_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM non_books WHERE category = ?", (category,))
        rows = cursor.fetchall()
        
        nonbooks = []
        for row in rows:
            item = {
                'Product ID': row['product_id'],
                'Product Name': row['product_name'],
                'Brand': row['brand'],
                'Price (PHP)': row['price_php'],
                'Product Description': row['product_description'],
                'Quantity': row['quantity'],
                'Category': row['category'],
                'Product Image Front': row['product_image_front'],
                'Product Image Back': row['product_image_back']
            }
            nonbooks.append(item)
        
        conn.close()
        return nonbooks
    except:
        return []

def search_nonbooks(query):
    """Search non-books by name, brand, or description"""
    try:
        with get_nonbooks_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM non_books 
            WHERE product_name LIKE ? OR brand LIKE ? OR product_description LIKE ?
            ORDER BY product_id
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        
        nonbooks = []
        for row in rows:
            item = {
                'Product ID': row['product_id'],
                'Product Name': row['product_name'],
                'Brand': row['brand'],
                'Price (PHP)': row['price_php'],
                'Product Description': row['product_description'],
                'Quantity': row['quantity'],
                'Category': row['category'],
                'Product Image Front': row['product_image_front'],
                'Product Image Back': row['product_image_back']
            }
            nonbooks.append(item)
        
        conn.close()
        return nonbooks
    except:
        return []

def get_nonbook_image_path(product_id, image_key="Product Image Front"):
    """Get non-book image path using database query"""
    try:
        with get_nonbooks_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        # Query specific fields we need
        cursor.execute("SELECT product_image_front, product_image_back, category FROM non_books WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return url_for('static', filename='images/placeholder.jpg')
        
        # Get filename and category from database
        filename = row['product_image_front'] if image_key == "Product Image Front" else row['product_image_back']
        category = row['category']
        
        conn.close()
        
        if not filename:
            return url_for('static', filename='images/placeholder.jpg')
        
        # Get folder mapping
        folder = NON_BOOK_CATEGORY_FOLDER_MAP.get(category, "novelties_images")
        
        # Check if image exists
        static_folder = os.path.join(current_app.root_path, 'static')
        rel_base = f'images/Nonbooks_Images/{folder}'
        
        for ext in ['jpg', 'png', 'webp', 'jpeg', 'JPG']:
            rel_path = f'{rel_base}/{filename}.{ext}'
            abs_path = os.path.join(static_folder, rel_path)
            if os.path.exists(abs_path):
                return url_for('static', filename=rel_path)
        
        return url_for('static', filename='images/placeholder.jpg')
        
    except:
        return url_for('static', filename='images/placeholder.jpg')

def get_books_image_path(product_id, image_key="Product Image Front"):
    try:
        with get_books_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        # Query specific fields we need
        cursor.execute("SELECT product_image_front, product_image_back, category FROM books WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return url_for('static', filename='images/placeholder.jpg')
        
        # Get filename and category from database
        filename = row['product_image_front'] if image_key == "Product Image Front" else row['product_image_back']
        category = row['category']
        
        conn.close()
        
        if not filename:
            return url_for('static', filename='images/placeholder.jpg')
        
        # Get folder mapping
        folder = BOOK_CATEGORY_FOLDER_MAP.get(category, "fiction_images")
        
        # Check if image exists
        static_folder = os.path.join(current_app.root_path, 'static')
        extensions = ['jpg', 'jpeg', 'png', 'webp', 'JPG', 'JPEG', 'PNG', 'WEBP']
        
        for ext in extensions:
            rel_path = f'images/Books_Images/{folder}/{filename}.{ext}'
            abs_path = os.path.join(static_folder, rel_path)
            if os.path.exists(abs_path):
                return url_for('static', filename=rel_path)
        
        return url_for('static', filename='images/placeholder.jpg')
        
    except:
        return url_for('static', filename='images/placeholder.jpg')

def get_trending(curr_section="books"):
    if curr_section == "books" or curr_section == "homepage":
        items = load_books()
    elif curr_section == "non_books":
        items = load_nonbooks()
    else:
        return []
    
    if not items:
        return []
    if len(items) <= 10:
        return items
    return random.sample(items, 10)