from flask import Blueprint, render_template, request, redirect, url_for
from utilities.load_items import (
    load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path, get_trending
)
from utilities.search_item import search_products
from constants import BOOK_CATEGORIES, NON_BOOK_CATEGORIES, CATEGORY_MAPPING

product_bp = Blueprint('product', __name__)

def extract_primary_category(category): 
    """Extract primary category from category string"""
    if ' - ' in category:
        return category.split(' - ')[0]
    return category

def apply_filters(products, price_filters, language_filters, is_book=True):
    """Apply price and language filters to products"""
    filtered_products = []
    
    for product in products:
        price = float(product.get('Price (PHP)', 0))
        
        price_match = not price_filters or not price_filters[0]
        if price_filters and price_filters[0]:
            price_range = price_filters[0]
            if price_range == '0-999.99' and 0 <= price <= 999.99:
                price_match = True
            elif price_range == '1000-1999.99' and 1000 <= price <= 1999.99:
                price_match = True
            elif price_range == '2000-above' and price >= 2000:
                price_match = True
            elif price_range == '0-499.99' and 0 <= price <= 499.99:
                price_match = True
            elif price_range == '500-999.99' and 500 <= price <= 999.99:
                price_match = True
            elif price_range == '1000-above' and price >= 1000:
                price_match = True
            else:
                price_match = False
        
        language_match = not language_filters or not language_filters[0] or not is_book
        if language_filters and language_filters[0] and is_book:
            product_language = product.get('Language', 'English').lower()
            language_match = product_language == language_filters[0].lower()
        
        if price_match and language_match:
            filtered_products.append(product)
    
    return filtered_products

@product_bp.route('/product/<int:product_id>')
def product_view(product_id):
    books = load_books()
    non_books = load_nonbooks()
    
    # Try to find in books first
    product = next((b for b in books if b.get('Product ID') == product_id), None)
    
    if product:
        product['image_path'] = get_books_image_path(product_id)
        product['back_image_path'] = get_books_image_path(product_id, image_key='Product Image Back')
        similar_products = get_trending(curr_section='books')
        for item in similar_products:
            item['image_path'] = get_books_image_path(item['Product ID'])
        return render_template('product_view.html', product=product, popular_items=similar_products, page_type='books')
    
    # Try non-books
    product = next((nb for nb in non_books if nb.get('Product ID') == product_id), None)
    
    if product:
        product['image_path'] = get_nonbook_image_path(product_id)
        product['back_image_path'] = get_nonbook_image_path(product_id, image_key='Product Image Back')
        similar_products = get_trending(curr_section='non_books')
        for item in similar_products:
            item['image_path'] = get_nonbook_image_path(item['Product ID'])
        return render_template('product_view.html', product=product, popular_items=similar_products, page_type='non_books')
    
    return "Product not found", 404

@product_bp.route('/category/<category_name>')
def category_products(category_name):
    """MISSING ROUTE: Category products listing"""
    books = load_books()
    non_books = load_nonbooks()
    
    price_filters = request.args.getlist('price')
    language_filters = request.args.getlist('language')

    actual_category = CATEGORY_MAPPING.get(category_name.lower(), category_name)

    filtered_books = [book for book in books if book.get("Category", "").lower().replace(" ", "-") == category_name.lower()]
    
    if price_filters or language_filters:
        filtered_books = apply_filters(filtered_books, price_filters, language_filters, is_book=True)
    
    for book in filtered_books: 
        book['image_path'] = get_books_image_path(book['Product ID'])

    filtered_non_books = []
    for non_book in non_books:
        category = non_book.get("Category", "")
        primary_category = extract_primary_category(category)
        
        if primary_category == actual_category:
            filtered_non_books.append(non_book)

    if price_filters:
        filtered_non_books = apply_filters(filtered_non_books, price_filters, [], is_book=False)

    for non_book in filtered_non_books:
        non_book['image_path'] = get_nonbook_image_path(non_book['Product ID'])

    updated_non_book_categories = NON_BOOK_CATEGORIES + ["drawing", "painting", "support"]
    
    if category_name.lower() in updated_non_book_categories:
        page_type = 'non_books'
    else:   
        page_type = 'books'

    all_products = filtered_books + filtered_non_books
    return render_template('components/product_list.html', 
                        category=category_name, 
                        products=all_products, 
                        non_book_categories=updated_non_book_categories, 
                        book_categories=BOOK_CATEGORIES, 
                        page_type=page_type)

@product_bp.route('/search')
def search():
    query = request.args.get('query', '').strip()
    
    if not query:
        return redirect(url_for('main.index'))
    
    price_filters = request.args.getlist('price')
    language_filters = request.args.getlist('language')
    
    search_results_books, search_results_non_books, total_results = search_products(
        query, price_filters, language_filters
    )
    
    all_results = search_results_books + search_results_non_books
    
    return render_template('components/search_results.html',
                        query=query,
                        products=all_results,
                        total_results=total_results,
                        non_book_categories=NON_BOOK_CATEGORIES,
                        book_categories=BOOK_CATEGORIES)