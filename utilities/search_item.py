from flask import request
from utilities.load_items import load_books, load_nonbooks, get_books_image_path, get_nonbook_image_path

def search_products(query, price_filters=None, language_filters=None):
    """
    Search for products based on query and apply filters
    
    Args:
        query (str): Search query string
        price_filters (list): List of price filter values
        language_filters (list): List of language filter values
    
    Returns:
        tuple: (search_results_books, search_results_non_books, total_count)
    """
    if not query or not query.strip():
        return [], [], 0
    
    books = load_books()
    non_books = load_nonbooks()
    
    # Initialize filter lists if None
    price_filters = price_filters or []
    language_filters = language_filters or []
    
    # Search in books
    search_results_books = []
    for book in books:
        if search_match(query, book, is_book=True):
            search_results_books.append(book)
    
    # Search in non-books
    search_results_non_books = []
    for non_book in non_books:
        if search_match(query, non_book, is_book=False):
            search_results_non_books.append(non_book)
    
    # Apply filters if any
    if price_filters or language_filters:
        search_results_books = apply_search_filters(search_results_books, price_filters, language_filters, is_book=True)
        search_results_non_books = apply_search_filters(search_results_non_books, price_filters, [], is_book=False)
    
    # Attach image paths
    for book in search_results_books:
        book['image_path'] = get_books_image_path(book['Product ID'])
    
    for non_book in search_results_non_books:
        non_book['image_path'] = get_nonbook_image_path(non_book['Product ID'])
    
    total_count = len(search_results_books) + len(search_results_non_books)
    
    return search_results_books, search_results_non_books, total_count

def search_match(query, product, is_book=True):
    """
    Check if product matches search query
    
    Args:
        query (str): Search query string
        product (dict): Product dictionary
        is_book (bool): Whether the product is a book or not
    
    Returns:
        bool: True if product matches query, False otherwise
    """
    if not query:
        return False
    
    query_lower = query.lower().strip()
    
    if is_book:
        # Search in book fields
        searchable_fields = [
            product.get('Book Name', ''),
            product.get('Author', ''),
            product.get('Category', ''),
            product.get('Language', ''),
            product.get('Description', ''),
            str(product.get('ISBN', '')),
            product.get('Publisher', ''),
            product.get('Series', ''),
        ]
    else:
        # Search in non-book fields
        searchable_fields = [
            product.get('Product Name', ''),
            product.get('Category', ''),
            product.get('Description', ''),
            product.get('Brand', ''),
            product.get('Model', ''),
            product.get('Color', ''),
        ]
    
    # Check if query matches any field
    for field in searchable_fields:
        if field and query_lower in field.lower():
            return True
    
    # Also check if it's a partial match for product names
    if is_book:
        book_name = product.get('Book Name', '').lower()
        if query_lower in book_name or any(word in book_name for word in query_lower.split()):
            return True
    else:
        product_name = product.get('Product Name', '').lower()
        if query_lower in product_name or any(word in product_name for word in query_lower.split()):
            return True
    
    return False

def apply_search_filters(products, price_filters, language_filters, is_book=True):
    """
    Apply price and language filters to search results
    
    Args:
        products (list): List of product dictionaries
        price_filters (list): List of price filter values
        language_filters (list): List of language filter values
        is_book (bool): Whether products are books or not
    
    Returns:
        list: Filtered list of products
    """
    if not price_filters and not language_filters:
        return products
    
    filtered_products = []
    
    for product in products:
        price = float(product.get('Price (PHP)', 0))
        
        # Price filtering - Handle single value from radio buttons
        price_match = not price_filters or price_filters[0] == ''  # If no price filter or empty string, match all
        if price_filters and price_filters[0]:  # If there's a price filter and it's not empty
            price_range = price_filters[0]  # Get the single selected value
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
        
        # Language filtering (only for books) - Handle single value
        language_match = not language_filters or language_filters[0] == '' or not is_book  # If no language filter, empty string, or not a book, match all
        if language_filters and language_filters[0] and is_book:  # If there's a language filter and it's a book and not empty
            product_language = product.get('Language', 'English').lower()
            language_match = product_language == language_filters[0].lower()
        
        if price_match and language_match:
            filtered_products.append(product)
    
    return filtered_products

def get_search_suggestions(query, limit=5):
    """
    Get search suggestions based on partial query
    
    Args:
        query (str): Partial search query
        limit (int): Maximum number of suggestions to return
    
    Returns:
        list: List of suggestion strings
    """
    if not query or len(query) < 2:
        return []
    
    books = load_books()
    non_books = load_nonbooks()
    suggestions = set()
    query_lower = query.lower()
    
    # Get suggestions from books
    for book in books:
        book_name = book.get('Book Name', '')
        author = book.get('Author', '')
        
        if book_name.lower().startswith(query_lower):
            suggestions.add(book_name)
        if author.lower().startswith(query_lower):
            suggestions.add(author)
        
        if len(suggestions) >= limit:
            break
    
    # Get suggestions from non-books if we need more
    if len(suggestions) < limit:
        for non_book in non_books:
            product_name = non_book.get('Product Name', '')
            brand = non_book.get('Brand', '')
            
            if product_name.lower().startswith(query_lower):
                suggestions.add(product_name)
            if brand.lower().startswith(query_lower):
                suggestions.add(brand)
            
            if len(suggestions) >= limit:
                break
    
    return list(suggestions)[:limit]

def search_by_category(category, query=None):
    """
    Search products within a specific category
    
    Args:
        category (str): Category name to search within
        query (str): Optional search query within the category
    
    Returns:
        tuple: (books, non_books, total_count)
    """
    books = load_books()
    non_books = load_nonbooks()
    
    # Filter by category first
    category_books = [book for book in books if book.get('Category', '').lower() == category.lower()]
    category_non_books = [nb for nb in non_books if category.lower() in nb.get('Category', '').lower()]
    
    # If there's a query, further filter by search
    if query and query.strip():
        filtered_books = []
        for book in category_books:
            if search_match(query, book, is_book=True):
                filtered_books.append(book)
        
        filtered_non_books = []
        for non_book in category_non_books:
            if search_match(query, non_book, is_book=False):
                filtered_non_books.append(non_book)
        
        category_books = filtered_books
        category_non_books = filtered_non_books
    
    # Attach image paths
    for book in category_books:
        book['image_path'] = get_books_image_path(book['Product ID'])
    
    for non_book in category_non_books:
        non_book['image_path'] = get_nonbook_image_path(non_book['Product ID'])
    
    total_count = len(category_books) + len(category_non_books)
    
    return category_books, category_non_books, total_count

def get_popular_searches():
    """
    Get list of popular/trending search terms
    
    Returns:
        list: List of popular search terms
    """
    return [
        "Fiction",
        "Romance",
        "Mystery",
        "Art Supplies",
        "Notebooks",
        "Planners",
        "Drawing",
        "Painting",
        "Bestsellers",
        "New Releases"
    ]