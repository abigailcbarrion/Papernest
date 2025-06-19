import sqlite3
import os

def view_database_schema(db_path):
    """View the schema of an SQLite database"""
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n=== SCHEMA FOR: {db_path} ===")
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in database.")
            conn.close()
            return
        
        # Display schema for each table
        for table in tables:
            table_name = table[0]
            print(f"\n--- TABLE: {table_name} ---")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                col_id, name, data_type, not_null, default_val, primary_key = col
                pk_marker = " (PRIMARY KEY)" if primary_key else ""
                null_marker = " NOT NULL" if not_null else ""
                default_marker = f" DEFAULT {default_val}" if default_val else ""
                print(f"  - {name}: {data_type}{null_marker}{default_marker}{pk_marker}")
        
        conn.close()
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"Error reading database: {e}")

def view_all_databases():
    """View schema for all databases in the data directory"""
    databases = [
        'data/users.db',
        'data/books.db', 
        'data/non_books.db'
    ]
    
    for db_path in databases:
        view_database_schema(db_path)

if __name__ == "__main__":
    # View all databases
    view_all_databases()
