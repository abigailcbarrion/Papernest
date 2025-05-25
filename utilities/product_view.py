from flask import render_template, request
from utilities.storage import load_books  

def get_product_view():
    books = load_books()
    product = books[0] if books else {}
    return render_template(
        'product_view.html',
        product=product,
        popular_books=books  
    )
