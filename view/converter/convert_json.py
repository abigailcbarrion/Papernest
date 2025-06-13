# Create data/convert_authors.py
import json
import sqlite3

def create_authors_database():
    # Load JSON data
    with open('data/featured_authors.json', 'r', encoding='utf-8') as f:
        authors_data = json.load(f)
    
    # Create SQLite database
    conn = sqlite3.connect('data/featured_authors.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS featured_authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bio TEXT,
            image_url TEXT,
            source_url TEXT,
            more_link TEXT,
            is_featured BOOLEAN DEFAULT 1
        );
    ''')
    
    # Insert data
    for author in authors_data['featured_authors']:
        cursor.execute('''
            INSERT INTO featured_authors (name, bio, image_url, source_url, more_link)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            author['name'],
            author['bio'],
            author['image_url'],
            author['source_url'],
            author['more_link']
        ))
    
    conn.commit()
    conn.close()
    print("Featured authors converted to SQLite!")

if __name__ == "__main__":
    create_authors_database()