function toggleSubmenu(event) {
    event.preventDefault();
    var submenu = document.getElementById('products-submenu');
    submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
}

document.getElementById('searchInput').addEventListener('keyup', filterProducts);
document.getElementById('categoryFilter').addEventListener('change', filterProducts);

function filterProducts() {
    const searchValue = document.getElementById('searchInput').value.toLowerCase();
    const categoryValue = document.getElementById('categoryFilter').value;
    const rows = document.querySelectorAll('#productsTable tbody tr');

    rows.forEach(row => {
        const name = row.getAttribute('data-name').toLowerCase();
        const category = row.getAttribute('data-category');

        const matchesSearch = name.includes(searchValue);
        const matchesCategory = !categoryValue || category === categoryValue;

        if (matchesSearch && matchesCategory) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function viewProduct(button) {
    const productId = button.getAttribute('data-product-id');
    const productType = button.getAttribute('data-product-type');
    const viewUrl = `/product/view/${productType}/${productId}`; // Adjust the URL structure as needed
    window.open(viewUrl, '_blank');
    console.log(`Viewing product with ID: ${productId}, Type: ${productType}`);
}

// function editProduct(button) {
//     const productType = button.getAttribute('data-product-type');
//     const editUrl = `/admin/products/advanced?product_type=${productType}`;
//     window.location.href = editUrl;
//     console.log(`Editing products of type: ${productType}`);
// }

function updateStock(button) {
    const productId = button.getAttribute('data-product-id');
    const productType = button.getAttribute('data-product-type');
    const currentStock = document.getElementById('stock-' + productId).textContent;
    const newStock = prompt('Enter new stock quantity:', currentStock);
    console.log(`Updating stock for product ID: ${productId}, Type: ${productType}, New Stock: ${newStock}`); // Debugging line

    if (newStock !== null && !isNaN(newStock)) {
        fetch('/admin/products/update-stock', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: parseInt(productId),
                product_type: productType,
                new_stock: parseInt(newStock)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('stock-' + productId).textContent = newStock;
                alert('Stock updated successfully');
            } else {
                alert('Error updating stock: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('Network error: ' + error.message);
        });
    }
}

function deleteProduct(button) {
    const productId = button.getAttribute('data-product-id');
    const productType = button.getAttribute('data-product-type');
    if (confirm(`Are you sure you want to delete this ${productType === 'book' ? 'book' : 'non-book'} product? This action cannot be undone.`)) {
        fetch('/admin/products/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                product_type: productType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`${productType === 'book' ? 'Book' : 'Non-book'} product deleted successfully`);
                location.reload();
            } else {
                alert('Error deleting product: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('Network error: ' + error.message);
        });
    }
}