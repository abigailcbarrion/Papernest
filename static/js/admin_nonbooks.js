function toggleSubmenu(event) {
  event.preventDefault();
  var submenu = document.getElementById('products-submenu');
  submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
}

// Search and filter functionality
document.getElementById('searchInput').addEventListener('keyup', filterProducts);
document.getElementById('categoryFilter').addEventListener('change', filterProducts);

function filterProducts() {
  const searchValue = document.getElementById('searchInput').value.toLowerCase();
  const categoryValue = document.getElementById('categoryFilter').value;
  const rows = document.querySelectorAll('#productsTable tbody tr[data-name]');
  
  rows.forEach(row => {
    const name = row.getAttribute('data-name');
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
  window.open("{{ url_for('product.product_view', product_id=0) }}".replace('0', productId), '_blank');
}

function editProduct(button)  {
  const productId = button.getAttribute('data-product-id');
  window.location.href = "{{ url_for('admin.admin_products2') }}" + "?edit=" + productId;
}

function updateStock(button) {
  const productId = button.getAttribute('data-product-id');
  const currentStock = document.getElementById('stock-' + productId).textContent;
  const newStock = prompt('Enter new stock quantity:', currentStock);
  
  if (newStock !== null && !isNaN(newStock)) {
    fetch("{{ url_for('admin.admin_products2') }}", {  // Use the same route
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product_id: parseInt(productId),
        product_type: 'non_book',
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
  if (confirm('Are you sure you want to delete this non-book product? This action cannot be undone.')) {
    fetch("{{ url_for('admin.delete_product') }}", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product_id: productId,
        product_type: 'non_book'
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('Non-book product deleted successfully');
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
