import json
import os

USERS_FILE = 'data/users.json'
BOOKS_FILE = 'data/books.json'

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_users():
    return load_json(USERS_FILE)

def save_users(users):
    save_json(USERS_FILE, users)

def load_books():
    return load_json(BOOKS_FILE)
