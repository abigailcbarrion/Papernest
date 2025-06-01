import os
from flask import url_for, current_app
from .storage import load_json
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
    "Supplies - Writing Instruments": "supplies_images",
}

BOOK_CATEGORY_FOLDER_MAP = {
    "Fiction": "fiction_images",
    "Non-fiction": "non-fiction_images",
    "Children's Books": "childrens-book_images",
    "Science and Technology": "science-technology_images",
    "Academic and Reference Development": "academics-book_images",
    "Self-Help and Personal Development": "self-help-book_images"
}   

def get_nonbook_image_path(item, image_key="Product Image Front"):
    filename = item.get(image_key)
    category = item.get("Category", "Other")
    folder = NON_BOOK_CATEGORY_FOLDER_MAP.get(category, "novelties_images")  # fallback to a default folder if not found

    static_folder = os.path.join(current_app.root_path, 'static')
    rel_base = f'images/Nonbooks_Images/{folder}'
    for ext in ['jpg', 'png', 'webp', 'jpeg', 'JPG']:
        rel_path = f'{rel_base}/{filename}.{ext}'
        abs_path = os.path.join(static_folder, rel_path)
        if os.path.exists(abs_path):
            return url_for('static', filename=rel_path)
    # fallback
    return url_for('static', filename='images/placeholder.jpg')


def get_books_image_path(item, image_key="Product Image Front"):
    filename = item.get(image_key)
    if not filename:
        print(f"[DEBUG] No image filename found for item: {item}")
        return url_for('static', filename='images/placeholder.jpg')

    category = item.get("Category", "Other").replace("&", "and").replace("-", " ").strip()
    possible_folders = []

    # Try mapped category folder first
    folder = BOOK_CATEGORY_FOLDER_MAP.get(category)
    if folder:
        possible_folders.append(f'images/Books_Images/{folder}')
    # Try all mapped folders (in case category is wrong/missing)
    possible_folders.extend([f'images/Books_Images/{f}' for f in BOOK_CATEGORY_FOLDER_MAP.values() if f not in possible_folders])
    # Try root Books_Images
    possible_folders.append('images/Books_Images')

    static_folder = os.path.join(current_app.root_path, 'static')
    extensions = ['jpg', 'jpeg', 'png', 'webp', 'JPG', 'JPEG', 'PNG', 'WEBP']

    tried_paths = []
    for folder in possible_folders:
        for ext in extensions:
            rel_path = f'{folder}/{filename}.{ext}'
            abs_path = os.path.join(static_folder, rel_path)
            if os.path.exists(abs_path):
                return url_for('static', filename=rel_path)
    # fallback
    print(f"[DEBUG] No valid image found for item: '{item.get('Book Name', filename)}'. Tried paths:")
    for path in tried_paths:
        print(f" - {path}")
    return url_for('static', filename='images/placeholder.jpg')


def get_trending(curr_section = "books"):

    if curr_section == "books" or curr_section == "homepage":
        items = load_json('data/books.json')
    elif curr_section == "non_books":
        items = load_json('data/non_books.json')
    else:
        return []
    
    if not items:
        return []
    if len(items) <= 10:
        return items
    return random.sample(items, 10)
