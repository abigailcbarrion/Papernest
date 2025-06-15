import sqlite3
import os
from flask import current_app

def get_db_connection(db_name):
    """Get database connection for specified database"""
    db_path = os.path.join(current_app.root_path, 'data', db_name)
    print(f"Database path: {os.path.abspath(db_path)}")
    return sqlite3.connect(db_path)

def get_users_db():
    return get_db_connection('users.db')

def get_books_db():
    return get_db_connection('books.db')

def get_nonbooks_db():
    return get_db_connection('non_books.db')

def get_authors_db():
    return get_db_connection('featured_authors.db')