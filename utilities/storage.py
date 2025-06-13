import json
import os
import sqlite3
from flask import current_app
from database_connection.connector import get_authors_db

def load_json(filepath):
    """Load data from JSON file"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_featured_author():
    try:
        db_path = os.path.join(current_app.root_path, 'data', 'featured_authors.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM featured_authors WHERE is_featured = 1 LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            author = {
                'name': row['name'],
                'bio': row['bio'],
                'image_url': row['image_url'],
                'source_url': row['source_url'],
                'more_link': row['more_link']
            }
            conn.close()
            return author
        
        conn.close()
        return None
    except:
        return None