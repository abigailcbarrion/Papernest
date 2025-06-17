// Cart page specific functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeCartPage();
});

function initializeCartPage() {
    // Only initialize if we're on the cart page
    if (document.querySelector('.cart-item-row')) {
        initializeDiscountToggle();
        initializeCartPageButtons();
    }
}

// ===========================================
// PRODUCT VIEW SPECIFIC CONTROLS
// ===========================================
function initializeProductViewControls() {
    const qtyInput = document.getElementById('product-qty');
    const decreaseBtn = document.getElementById('decrease-qty');
    const increaseBtn = document.getElementById('increase-qty');
    
    if (decreaseBtn) {
        decreaseBtn.onclick = function() {
            e.preventDefault();
            let val = parseInt(qtyInput.value, 10);
            if (val > 1) {
                qtyInput.value = val - 1
            }
        };
    }
    
    if (increaseBtn) {
        increaseBtn.onclick = function() {
            e.preventDefault();
            let val = parseInt(qtyInput.value, 10);
            qtyInput.value = val + 1;
        };
    }
}

// ===========================================
// CART PAGE SPECIFIC FUNCTIONS
// ===========================================
function initializeDiscountToggle() {
    const discountBtn = document.querySelector('#DiscountBtn button');
    if (discountBtn) {
        discountBtn.addEventListener('click', function() {
            toggleDiscountSection(this);
        });
    }
}

function initializeCartPageButtons() {
    document.querySelectorAll('.btn-increase').forEach(button => {
        button.addEventListener('click', function() {
            updateCartQuantity(this, 1);
        });
    });
    
    document.querySelectorAll('.btn-decrease').forEach(button => {
        button.addEventListener('click', function() {
            updateCartQuantity(this, -1);
        });
    });
    
    document.querySelectorAll('.btn-remove').forEach(button => {
        button.addEventListener('click', function() {
            removeFromCart(this);
        });
    });
}

function updateCartQuantity(button, change) {
    const row = button.closest('.cart-item-row');
    const quantityInput = row.querySelector('.quantity-input');
    const productId = parseInt(row.dataset.productId);
    const productType = row.dataset.productType;
    
    let newQuantity = parseInt(quantityInput.value) + change;
    if (newQuantity < 1) newQuantity = 1;
    
    button.disabled = true;
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
            quantityInput.value = newQuantity;
            updateItemSubtotal(row, newQuantity, getItemPrice(row));
            updateCartTotal();
            showNotification('Cart updated', 'success');
        } else {
            showNotification(data.message || 'Error updating quantity', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating quantity:', error);
        showNotification('Error updating quantity', 'error');
    })
    .finally(() => {
        button.disabled = false;
        button.style.opacity = '1';
    });
}

function removeFromCart(button) {
    const row = button.closest('.cart-item-row');
    const productId = parseInt(row.dataset.productId);
    const productType = row.dataset.productType;
    const itemName = row.querySelector('.item-name').textContent;
    
    if (!confirm(`Remove "${itemName}" from cart?`)) return;
    
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
            row.style.transition = 'all 0.3s ease';
            row.style.transform = 'translateX(-100%)';
            row.style.opacity = '0';
            
            setTimeout(() => {
                row.remove();
                updateCartTotal();
                checkEmptyCart();
            }, 300);
            
            showNotification('Item removed from cart', 'success');
        } else {
            showNotification(data.message || 'Error removing item', 'error');
            row.style.opacity = '1';
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error removing item:', error);
        showNotification('Error removing item', 'error');
        row.style.opacity = '1';
        button.disabled = false;
    });
}

// ===========================================
// CART PAGE UTILITY FUNCTIONS
// ===========================================
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

function getItemPrice(row) {
    const priceElement = row.querySelector('.item-price');
    const quantityInput = row.querySelector('.quantity-input');
    
    if (priceElement && quantityInput) {
        const totalPrice = parseFloat(priceElement.textContent.replace('₱', ''));
        const quantity = parseInt(quantityInput.value);
        return quantity > 0 ? totalPrice / quantity : 0;
    }
    return 0;
}

function updateItemSubtotal(row, quantity, unitPrice) {
    const priceElement = row.querySelector('.item-price');
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
    
    const subtotalElement = document.querySelector('.subtotal-price');
    const totalElement = document.querySelector('.total-price b');
    
    if (subtotalElement) subtotalElement.textContent = `₱${total.toFixed(2)}`;
    if (totalElement) totalElement.textContent = `₱${total.toFixed(2)}`;
}

function checkEmptyCart() {
    const cartRows = document.querySelectorAll('.cart-item-row');
    if (cartRows.length === 0) {
        setTimeout(() => window.location.reload(), 500);
    }
}

// Global functions for backward compatibility
window.DiscountBtn = toggleDiscountSection;
window.updateQuantity = updateCartQuantity;
window.removeFromCart = removeFromCart;