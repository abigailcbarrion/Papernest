/**
 * Billing page functionality
 * Handles payment methods and popups for different payment options
 */

document.addEventListener('DOMContentLoaded', function() {
    // Set today's date for order confirmation
    document.getElementById('order-date').textContent = new Date().toLocaleDateString();
    
    // Generate random order number
    document.getElementById('order-number').textContent = '#ORD-' + Math.floor(100000 + Math.random() * 900000);
    
    // Initialize payment popups
    initializePaymentPopups();
    
    // Initialize form formatting
    initializeFormFormatting();

    //handle image loading errors

    document.querySelectorAll('.wallet-image').forEach(img => {
        img.addEventListener('error', function(){
            const fallbackSrc = this.getAttribute('data-fallback');
            if(fallbackSrc){
                this.src = fallbackSrc;
            }

            this.removeEventListener('error', arguments.callee);
        })
    })
});

/**
 * Initialize payment popups and related functionality
 */
function initializePaymentPopups() {
    // Get DOM elements
    const processPaymentBtn = document.getElementById('process-payment-btn');
    const paymentMethods = document.querySelectorAll('input[name="payment"]');
    const billingForm = document.getElementById('billing-form');
    
    // Payment popups
    const cardPopup = document.getElementById('card-payment-popup');
    const digitalWalletPopup = document.getElementById('digital-wallet-popup');
    const codPopup = document.getElementById('cod-confirmation-popup');
    const gcashPopup = document.getElementById('gcash-payment-popup');
    const paymayaPopup = document.getElementById('paymaya-payment-popup');
    const successPopup = document.getElementById('order-success-popup');
    
    // Initialize close buttons for all popups
    initializePopupCloseButtons();
    
    // Process payment button
    processPaymentBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        const selectedPayment = document.querySelector('input[name="payment"]:checked').value;
        
        // Show appropriate popup based on selection
        if (selectedPayment === 'card') {
            openPopup(cardPopup);
        } else if (selectedPayment === 'digital_wallet') {
            openPopup(digitalWalletPopup);
        } else if (selectedPayment === 'cod') {
            openPopup(codPopup);
        }
    });
    
    // Initialize e-wallet selection
    initializeEWalletSelection();
    
    // Card payment form submission
    document.getElementById('card-payment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateCardForm()) {
            closePopup(cardPopup);
            finalizeOrder('Credit/Debit Card');
        }
    });
    // Digital wallet form submission
    document.getElementById('digital-wallet-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const refNumber = document.getElementById('wallet-ref-number').value.trim();
        if (!refNumber) {
            showMessage('Please enter the reference number.');
            return;
        }
        closePopup(document.getElementById('digital-wallet-popup'));
        finalizeOrder('Digital Wallet', refNumber);
    });
    
    // GCash payment form submission
    // document.getElementById('gcash-payment-form').addEventListener('submit', function(e) {
    //     e.preventDefault();
        
    //     if (validateMobileForm('gcash')) {
    //         closePopup(gcashPopup);
    //         finalizeOrder('GCash');
    //     }
    // });
    
    // PayMaya payment form submission
    // document.getElementById('paymaya-payment-form').addEventListener('submit', function(e) {
    //     e.preventDefault();
        
    //     if (validateMobileForm('paymaya')) {
    //         closePopup(paymayaPopup);
    //         finalizeOrder('PayMaya');
    //     }
    // });
    
    // COD confirmation button
    document.getElementById('confirm-cod-btn').addEventListener('click', function() {
        closePopup(codPopup);
        finalizeOrder('Cash on Delivery');
    });
    
    let redirectTimer;
    // View order button in success popup
    document.getElementById('view-order-btn').addEventListener('click', function() {
        clearTimeout(redirectTimer);
        
        // Set localStorage flag to show orders tab
        localStorage.setItem('showOrdersTab', 'true');
        
        // Redirect directly to account page
        window.location.href = '/account?section=orders';
    });
}

/**
 * Initialize close buttons for all popups
 */
function initializePopupCloseButtons() {
    document.querySelectorAll('.popup-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const popup = this.closest('.popup-overlay');
            closePopup(popup);
        });
    });
}

/**
 * Initialize e-wallet selection functionality
 */
function initializeEWalletSelection() {
    const eWalletOptions = document.querySelectorAll('.e-wallet-option');
    const continueButton = document.getElementById('select-wallet-btn');
    let selectedWallet = null;
    
    // Add event listeners to e-wallet options
    eWalletOptions.forEach(option => {
        option.addEventListener('click', function() {
            eWalletOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            selectedWallet = this.getAttribute('data-wallet');
            continueButton.disabled = false;
        });
    });
    
    // E-wallet continue button
    continueButton.addEventListener('click', function() {
        const digitalWalletPopup = document.getElementById('digital-wallet-popup');
        closePopup(digitalWalletPopup);
        
        if (selectedWallet === 'gcash') {
            openPopup(document.getElementById('gcash-payment-popup'));
        } else if (selectedWallet === 'paymaya') {
            openPopup(document.getElementById('paymaya-payment-popup'));
        }
    });
}

/**
 * Initialize input formatting for card fields
 */
function initializeFormFormatting() {
    // Format credit card number with spaces
    const cardNumberInput = document.getElementById('card-number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            if (value.length > 16) {
                value = value.substr(0, 16);
            }
            
            // Add spaces after every 4 digits
            const formattedValue = value.replace(/(.{4})/g, '$1 ').trim();
            e.target.value = formattedValue;
        });
    }
    
    // Format expiry date with slash
    const expiryInput = document.getElementById('card-expiry');
    if (expiryInput) {
        expiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\//g, '');
            
            if (value.length > 2) {
                value = value.substr(0, 2) + '/' + value.substr(2, 2);
            }
            
            e.target.value = value;
        });
    }
}

/**
 * Open a popup
 * @param {HTMLElement} popup - The popup element to open
 */
function openPopup(popup) {
    popup.classList.add('active');
}

/**
 * Close a popup
 * @param {HTMLElement} popup - The popup element to close
 */
function closePopup(popup) {
    popup.classList.remove('active');
}

/**
 * Validate credit card form
 * @returns {boolean} - Whether the form is valid
 */
function validateCardForm() {
    const cardNumber = document.getElementById('card-number').value.replace(/\s/g, '');
    const cardExpiry = document.getElementById('card-expiry').value;
    const cardCvv = document.getElementById('card-cvv').value;
    const cardName = document.getElementById('card-name').value;
    
    if (!cardName) {
        showMessage('Please enter cardholder name');
        return false;
    }
    
    if (!/^\d{16}$/.test(cardNumber)) {
        showMessage('Please enter a valid 16-digit card number');
        return false;
    }
    
    if (!/^\d{2}\/\d{2}$/.test(cardExpiry)) {
        showMessage('Please enter a valid expiry date (MM/YY)');
        return false;
    }
    
    if (!/^\d{3,4}$/.test(cardCvv)) {
        showMessage('Please enter a valid CVV code');
        return false;
    }
    
    return true;
}

/**
 * Validate mobile payment form
 * @param {string} type - The payment type ('gcash' or 'paymaya')
 * @returns {boolean} - Whether the form is valid
 */
function validateMobileForm(type) {
    const numberField = document.getElementById(`${type}-number`);
    const nameField = document.getElementById(`${type}-name`);
    
    if (!nameField.value) {
        showMessage('Please enter your account name');
        return false;
    }
    
    if (!/^09\d{9}$/.test(numberField.value)) {
        showMessage('Please enter a valid mobile number (e.g., 09XXXXXXXXX)');
        return false;
    }
    
    return true;
}

/**
 * Show a message to the user
 * @param {string} message - The message to display
 */
function showMessage(message) {
    alert(message); // Simple implementation - could be replaced with a toast notification
}

/**
 * Process the order with the selected payment method
 * @param {string} paymentMethod - The selected payment method
 */
function finalizeOrder(paymentMethod, refNumber = '') {
    // Get the user ID from our hidden maintainer
    const userIdMaintainer = document.getElementById('user-id-maintainer');
    const userId = userIdMaintainer ? userIdMaintainer.dataset.userId : null;
    const username = userIdMaintainer ? userIdMaintainer.dataset.username : null;
    
    // Set payment method in order summary
    document.getElementById('order-payment-method').textContent = paymentMethod;
    
    // Create the payment data
    const paymentData = {
        payment_method: paymentMethod,
        user_id: userId,   // Include user ID from the hidden field
        username: username, // Include username from the hidden field
        reference_number: refNumber
    };
    
    // Use fetch to send the payment data
    fetch('/process-payment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(paymentData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show the success popup
            document.getElementById('order-number').textContent = `#${data.order_id}`;
            openPopup(document.getElementById('order-success-popup'));
            
            // Set localStorage flag for account page
            localStorage.setItem('showOrdersTab', 'true');
        } else {
            showMessage(data.message || 'Payment processing failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('An error occurred while processing your payment');
    });
    
    // Show the success popup
    openPopup(document.getElementById('order-success-popup'));
}

/**
 * Submit a form via AJAX and then redirect
 * @param {HTMLFormElement} form - The form to submit
 * @param {string} redirectUrl - Where to redirect after submission
 */
function submitFormWithAjax(form, redirectUrl) {
    // Create a new hidden form for submission
    const hiddenForm = document.createElement('form');
    hiddenForm.method = 'POST';
    hiddenForm.action = form.action;
    hiddenForm.style.display = 'none';
    
    // Copy all fields from the original form
    const formData = new FormData(form);
    for (const [name, value] of formData.entries()) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        hiddenForm.appendChild(input);
    }
    
    // Add a field to indicate the redirect URL
    const redirectInput = document.createElement('input');
    redirectInput.type = 'hidden';
    redirectInput.name = 'redirect_url';
    redirectInput.value = redirectUrl;
    hiddenForm.appendChild(redirectInput);
    
    // Append to document and submit
    document.body.appendChild(hiddenForm);
    hiddenForm.submit();
}