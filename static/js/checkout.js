/**
 * Papernest Checkout System
 * Handles checkout page functionality including:
 * - Processing selected items from cart
 * - Calculating order totals
 * - Form validation
 * - Address management
 */

// ===========================================
// INITIALIZATION
// ===========================================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize selected items processing
    processSelectedItems();
    
    // Initialize address form functionality
    initializeAddressForms();
    
    // Initialize form validation
    initializeFormValidation();
});

// ===========================================
// SELECTED ITEMS PROCESSING
// ===========================================
/**
 * Process items that were selected on the cart page
 */
function processSelectedItems() {
    // Check if we're processing only selected items
    const urlParams = new URLSearchParams(window.location.search);
    const selectedOnly = urlParams.get('selected') === 'true';
    
    if (!selectedOnly) return;
    
    // Get selected items from sessionStorage
    const selectedItems = JSON.parse(sessionStorage.getItem('selectedItems') || '[]');
    
    if (selectedItems.length <= 0) return;
    
    // Process only selected items
    const allItems = document.querySelectorAll('.checkout-item');
    let anyVisible = false;
    
    // Create hidden inputs to pass selected product IDs to server
    const form = document.querySelector('#checkout-form');
    
    allItems.forEach(item => {
        const productId = item.getAttribute('data-product-id');
        const productType = item.getAttribute('data-product-type');
        
        // Check if this item was selected
        const selectedItem = selectedItems.find(selected => 
            selected.product_id.toString() === productId && 
            selected.product_type === productType
        );
        
        if (selectedItem) {
            // Show this item
            item.style.display = 'flex';
            anyVisible = true;
            
            // Update quantity if needed
            updateItemQuantity(item, selectedItem.quantity);
            
            // Add hidden input to form to pass this product ID to server
            addHiddenProductInput(form, productId);
        } else {
            // Hide non-selected items
            item.style.display = 'none';
        }
    });
    
    // Handle case with no visible items
    handleEmptyCheckout(anyVisible);
    
    // Update totals to reflect only selected items
    updateCheckoutTotals();
}

/**
 * Updates item quantity display in checkout
 * @param {HTMLElement} itemElement - The checkout item element
 * @param {number} quantity - The new quantity value
 */
function updateItemQuantity(itemElement, quantity) {
    if (!quantity) return;
    
    const qtyElement = itemElement.querySelector('.checkout-item-quantity');
    if (qtyElement) {
        qtyElement.textContent = quantity;
    }
}

/**
 * Adds a hidden form input for selected products
 * @param {HTMLFormElement} form - The checkout form 
 * @param {string} productId - The product ID to add
 */
function addHiddenProductInput(form, productId) {
    if (!form) return;
    
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'selected_products';
    input.value = productId;
    form.appendChild(input);
}

/**
 * Handle case when no items are selected for checkout
 * @param {boolean} anyVisible - Whether any items are visible
 */
function handleEmptyCheckout(anyVisible) {
    if (anyVisible) return;
    
    const container = document.querySelector('.checkout-items-container');
    if (container) {
        container.innerHTML = '<div class="empty-checkout">' +
            'No items selected. <a href="/cart">Return to cart</a> and select items to checkout.</div>';
    }
    
    const checkoutBtn = document.querySelector('#place-order-btn');
    if (checkoutBtn) {
        checkoutBtn.disabled = true;
    }
}

// ===========================================
// ORDER TOTAL CALCULATIONS
// ===========================================
/**
 * Calculates and updates all order totals
 */
function updateCheckoutTotals() {
    // Calculate total from visible items only
    let subtotal = calculateSubtotal();
    
    // Update the subtotal display
    updateSubtotalDisplay(subtotal);
    
    // Update final total
    updateTotalAmount(subtotal);
}

/**
 * Calculates the order subtotal from visible items
 * @returns {number} - The calculated subtotal
 */
function calculateSubtotal() {
    let subtotal = 0;
    const visibleItems = document.querySelectorAll('.checkout-item[style="display: flex;"]');
    
    visibleItems.forEach(item => {
        const priceText = item.querySelector('.checkout-item-price').textContent.trim();
        const price = parseFloat(priceText.replace('₱', '').replace(',', ''));
        
        const qtyText = item.querySelector('.checkout-item-quantity').textContent.trim();
        const quantity = parseInt(qtyText);
        
        if (!isNaN(price) && !isNaN(quantity)) {
            subtotal += price * quantity;
        }
    });
    
    return subtotal;
}

/**
 * Updates the subtotal display
 * @param {number} subtotal - The subtotal amount
 */
function updateSubtotalDisplay(subtotal) {
    const subtotalElement = document.querySelector('.checkout-subtotal');
    if (subtotalElement) {
        subtotalElement.textContent = `₱${subtotal.toFixed(2)}`;
    }
}

/**
 * Updates the total amount including shipping
 * @param {number} subtotal - The subtotal amount
 */
function updateTotalAmount(subtotal) {
    const shippingElement = document.querySelector('.checkout-shipping-fee');
    const totalElement = document.querySelector('.checkout-total');
    
    if (!totalElement) return;
    
    let shippingFee = 0;
    if (shippingElement) {
        const shippingText = shippingElement.textContent.trim();
        shippingFee = parseFloat(shippingText.replace('₱', '').replace(',', '')) || 0;
    }
    
    const total = subtotal + shippingFee;
    totalElement.textContent = `₱${total.toFixed(2)}`;
}

// ===========================================
// ADDRESS FORM MANAGEMENT
// ===========================================
/**
 * Initialize address form functionality
 */
function initializeAddressForms() {
    // Initialize same address checkbox
    const sameAddressCheckbox = document.getElementById('same-address');
    if (sameAddressCheckbox) {
        sameAddressCheckbox.addEventListener('change', toggleBillingAddressFields);
        // Initialize state on page load
        toggleBillingAddressFields();
    }
}

/**
 * Toggle billing address section visibility and copy values
 */
function toggleBillingAddressFields() {
    const checkbox = document.getElementById('same-address');
    const billingSection = document.querySelector('.billing-address-section');
    
    if (!checkbox || !billingSection) return;
    
    if (checkbox.checked) {
        billingSection.classList.add('hidden');
        copyShippingToBillingFields();
    } else {
        billingSection.classList.remove('hidden');
    }
}

/**
 * Copy shipping address values to billing fields
 */
function copyShippingToBillingFields() {
    document.querySelectorAll('.shipping-field').forEach(field => {
        const billingField = document.getElementById('billing_' + field.id);
        if (billingField) {
            billingField.value = field.value;
        }
    });
}

// ===========================================
// FORM VALIDATION
// ===========================================
/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Initialize form validation
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            if (!validateCheckoutForm()) {
                e.preventDefault();
            }
        });
    }
    
    // Add input event listeners to required fields
    document.querySelectorAll('.required-field').forEach(field => {
        field.addEventListener('input', function() {
            // Remove error styling when user starts typing
            this.classList.remove('error-field');
            const errorMsg = this.parentNode.querySelector('.error-message');
            if (errorMsg) errorMsg.remove();
        });
    });
}

/**
 * Validate all checkout form fields
 * @returns {boolean} - Whether form is valid
 */
function validateCheckoutForm() {
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.error-message').forEach(el => el.remove());
    
    // Validate required fields
    isValid = validateRequiredFields() && isValid;
    
    // Validate specific field formats
    isValid = validateEmailFormat() && isValid;
    isValid = validatePhoneFormat() && isValid;
    
    return isValid;
}

/**
 * Validate all required fields have values
 * @returns {boolean} - Whether all required fields are valid
 */
function validateRequiredFields() {
    let isValid = true;
    const requiredFields = document.querySelectorAll('.required-field');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            showFieldError(field, 'This field is required');
        }
    });
    
    return isValid;
}

/**
 * Validate email format
 * @returns {boolean} - Whether email format is valid
 */
function validateEmailFormat() {
    let isValid = true;
    const emailField = document.querySelector('input[type="email"]');
    
    if (emailField && emailField.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            isValid = false;
            showFieldError(emailField, 'Please enter a valid email address');
        }
    }
    
    return isValid;
}

/**
 * Validate phone number format
 * @returns {boolean} - Whether phone format is valid
 */
function validatePhoneFormat() {
    let isValid = true;
    const phoneField = document.querySelector('input[name="phone"]');
    
    if (phoneField && phoneField.value) {
        const phoneRegex = /^\d{10,15}$/;
        if (!phoneRegex.test(phoneField.value.replace(/[^0-9]/g, ''))) {
            isValid = false;
            showFieldError(phoneField, 'Please enter a valid phone number');
        }
    }
    
    return isValid;
}

/**
 * Display error message for a form field
 * @param {HTMLElement} field - The form field with error
 * @param {string} message - The error message to display
 */
function showFieldError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#e74c3c';
    errorDiv.style.fontSize = '0.8em';
    errorDiv.style.marginTop = '5px';
    
    field.classList.add('error-field');
    field.parentNode.appendChild(errorDiv);
}