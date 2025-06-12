import sqlite3
import os

def view_all_users():
    """Simple view of all users in the database"""
    db_path = os.path.join('data', 'users.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
            return
        
        print(f"\nFOUND {len(users)} USERS:")
        print("=" * 100)
        
        for i, user in enumerate(users, 1):
            print(f"\nUSER #{i}:")
            print("-" * 50)
            for key in user.keys():
                try:
                    value = user[key] if user[key] else 'N/A'
                    print(f"{key}: {value}")
                except:
                    print(f"{key}: N/A")
            print("-" * 50)
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_all_users()