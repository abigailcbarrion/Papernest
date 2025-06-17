document.addEventListener('DOMContentLoaded', function() {
    initializeCartPage();
});

function initializeCartPage() {
    initializeDiscountToggle();
    initializeQuantityButtons();
    initializeRemoveButtons();
}

// Discount toggle functionality
function initializeDiscountToggle() {
    const discountBtn = document.querySelector('#DiscountBtn button');
    
    if (discountBtn) {
        discountBtn.addEventListener('click', function() {
            toggleDiscountSection(this);
        });
    }
}

function toggleDiscountSection(button) {
    const discountDiv = document.getElementById("myDiv");
    
    if (!discountDiv) return;
    
    if (discountDiv.style.display === "none" || discountDiv.style.display === "") {
        discountDiv.style.display = "flex";
    } else {
        discountDiv.style.display = "none";
    }
    
    const icon = button.querySelector("i");
    if (icon) {
        icon.classList.toggle("fa-chevron-down");
        icon.classList.toggle("fa-chevron-up");
    }
}

// Quantity control functionality
function initializeQuantityButtons() {
    document.querySelectorAll('.btn-increase').forEach(button => {
        button.addEventListener('click', function() {
            updateQuantity(this, 1);
        });
    });
    
    document.querySelectorAll('.btn-decrease').forEach(button => {
        button.addEventListener('click', function() {
            updateQuantity(this, -1);
        });
    });
}

function updateQuantity(button, change) {
    const row = button.closest('.cart-item-row');
    const quantityInput = row.querySelector('.quantity-input');
    const productId = parseInt(row.dataset.productId);
    const productType = row.dataset.productType;
    
    let newQuantity = parseInt(quantityInput.value) + change;
    if (newQuantity < 1) newQuantity = 1;
    
    // Add loading state
    button.disabled = true;
    const originalOpacity = button.style.opacity;
    button.style.opacity = '0.5';
    
    fetch('/cart/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            product_id: productId,
            product_type: productType,
            quantity: newQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the input value
            quantityInput.value = newQuantity;
            
            // Update the subtotal for this item
            updateItemSubtotal(row, newQuantity, data.item_price || getItemPrice(row));
            
            // Update the total
            updateCartTotal();
            
            showCartNotification('Cart updated successfully', 'success');
        } else {
            showCartNotification(data.message || 'Error updating quantity', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating quantity:', error);
        showCartNotification('Error updating quantity', 'error');
    })
    .finally(() => {
        button.disabled = false;
        button.style.opacity = originalOpacity;
    });
}

// Remove item functionality
function initializeRemoveButtons() {
    document.querySelectorAll('.btn-remove').forEach(button => {
        button.addEventListener('click', function() {
            removeFromCart(this);
        });
    });
}

function removeFromCart(button) {
    const row = button.closest('.cart-item-row');
    const productId = parseInt(row.dataset.productId);
    const productType = row.dataset.productType;
    const itemName = row.querySelector('.item-name').textContent;
    
    if (!confirm(`Remove "${itemName}" from cart?`)) {
        return;
    }
    
    // Add loading state
    button.disabled = true;
    row.style.opacity = '0.5';
    
    fetch('/cart/remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            product_id: productId,
            product_type: productType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Animate row removal
            row.style.transition = 'all 0.3s ease';
            row.style.transform = 'translateX(-100%)';
            row.style.opacity = '0';
            
            setTimeout(() => {
                row.remove();
                updateCartTotal();
                checkEmptyCart();
            }, 300);
            
            showCartNotification('Item removed from cart', 'success');
        } else {
            showCartNotification(data.message || 'Error removing item', 'error');
            row.style.opacity = '1';
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error removing item:', error);
        showCartNotification('Error removing item', 'error');
        row.style.opacity = '1';
        button.disabled = false;
    });
}

// Helper functions
function getItemPrice(row) {
    // Extract price from the current price display
    const priceElement = row.querySelector('.item-price');
    const quantityInput = row.querySelector('.quantity-input');
    
    if (priceElement && quantityInput) {
        const totalPrice = parseFloat(priceElement.textContent.replace('₱', ''));
        const quantity = parseInt(quantityInput.value);
        return quantity > 0 ? totalPrice / quantity : 0;
    }
    return 0;
}

function updateItemSubtotal(row, quantity, unitPrice = null) {
    const priceElement = row.querySelector('.item-price');
    
    if (!unitPrice) {
        unitPrice = getItemPrice(row);
    }
    
    const newSubtotal = unitPrice * quantity;
    
    if (priceElement) {
        priceElement.textContent = `₱${newSubtotal.toFixed(2)}`;
    }
}

function updateCartTotal() {
    let total = 0;
    
    document.querySelectorAll('.cart-item-row').forEach(row => {
        const priceElement = row.querySelector('.item-price');
        
        if (priceElement) {
            const price = parseFloat(priceElement.textContent.replace('₱', ''));
            total += price;
        }
    });
    
    // Update total display
    const subtotalElement = document.querySelector('.subtotal-price');
    const totalElement = document.querySelector('.total-price b');
    
    if (subtotalElement) {
        subtotalElement.textContent = `₱${total.toFixed(2)}`;
    }
    
    if (totalElement) {
        totalElement.textContent = `₱${total.toFixed(2)}`;
    }
}

function checkEmptyCart() {
    const cartRows = document.querySelectorAll('.cart-item-row');
    
    if (cartRows.length === 0) {
        // Reload page to show empty cart message
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
}

function showCartNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `cart-notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ${type === 'success' ? 'background: #4CAF50;' : 'background: #f44336;'}
    `;
    
    document.body.appendChild(notification);
    
    // Fade in
    setTimeout(() => notification.style.opacity = '1', 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Discount button functionality (legacy support)
function DiscountBtn(button) {
    toggleDiscountSection(button);
}

// Global functions for backward compatibility and direct HTML onclick handlers
window.DiscountBtn = DiscountBtn;
window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart;
window.toggleDiscountSection = toggleDiscountSection;