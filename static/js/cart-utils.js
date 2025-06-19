// ===========================================
// CORE CART FUNCTIONS
// ===========================================
function addToCart(productId, productType, productName, price, imagePath, quantity, button) {
    console.log('=== ADD TO CART CALLED ===');
    console.log('Product ID:', productId);
    console.log('Product Type:', productType);
    console.log('Quantity:', quantity);
    
    checkUserAuthentication()
        .then(isLoggedIn => {
            console.log('User authenticated:', isLoggedIn);
            
            if (!isLoggedIn) {
                showLoginDialog();
                return;
            }
            
            const originalText = button.textContent;
            const removeLoadingState = addButtonLoadingState(button, originalText);

            const cartData = {
                product_id: productId,
                product_type: productType,
                product_name: productName,
                price: price,
                image_path: imagePath,
                quantity: quantity
            };

            console.log('Sending cart data:', cartData);

            fetch('/cart/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(cartData)
            })
            .then(response => {
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    return response.text().then(errorText => {
                        console.error('Server error response:', errorText);
                        throw new Error(`HTTP error! status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Success response:', data);
                
                if (data.success) {
                    const message = quantity > 1 ? `${quantity} items added to cart!` : 'Product added to cart!';
                    showNotification(message, 'success');
                    updateCartCount();
                    removeLoadingState(true);
                } else {
                    showNotification(data.message || 'Failed to add to cart', 'error');
                    removeLoadingState(false);
                }
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
                showNotification('Error adding to cart', 'error');
                removeLoadingState(false);
            });
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
            showLoginDialog();
        });
}

function addToWishlist(productId, productType, button) {
    console.log('=== ADD TO WISHLIST CALLED ===');
    console.log('Product ID:', productId);
    console.log('Product Type:', productType);
    
    checkUserAuthentication()
        .then(isLoggedIn => {
            if (!isLoggedIn) {
                showLoginDialog();
                return;
            }
            
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            button.disabled = true;
            
            const wishlistData = {
                product_id: productId,
                product_type: productType
            };
            
            fetch('/wishlist/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(wishlistData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Product added to wishlist!', 'success');
                    
                    // Update button appearance
                    button.classList.add('active');
                    button.innerHTML = '<i class="fas fa-heart"></i>';
                    button.style.background = '#ff4757';
                    button.style.color = 'white';
                    button.style.border = '2px solid #ff4757';
                    button.title = 'Remove from Wishlist';
                    button.disabled = false; 
                    
                    // Button animation
                    button.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        button.style.transform = 'scale(1)';
                    }, 200);
                } else {
                    showNotification(data.message || 'Failed to add to wishlist', 'error');
                    button.innerHTML = originalHTML;
                    button.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error adding to wishlist:', error);
                showNotification('Error adding to wishlist', 'error');
                button.innerHTML = originalHTML;
                button.disabled = false;
            });
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
            showLoginDialog();
        });
}

// ===========================================
// UTILITY FUNCTIONS
// ===========================================
function checkUserAuthentication() {
    return fetch('/auth/check', {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => data.authenticated)
    .catch(() => false);
}

function showLoginDialog() {
    if (typeof showLoginPopup === 'function') {
        showLoginPopup();
    } else if (typeof window.showLoginPopup === 'function') {
        window.showLoginPopup();
    } else {
        const shouldLogin = confirm('Please log in to add items to your cart. Would you like to go to the login page?');
        if (shouldLogin) {
            window.location.href = '/';
        }
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    let backgroundColor;
    switch (type) {
        case 'success':
            backgroundColor = '#4CAF50';
            break;
        case 'error':
            backgroundColor = '#f44336';
            break;
        case 'info':
            backgroundColor = '#2196F3';
            break;
        default:
            backgroundColor = '#4CAF50';
    }

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
        background: ${backgroundColor};
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.style.opacity = '1', 100);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

function updateCartCount() {
    fetch('/cart/count', {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement && data.count !== undefined) {
            cartCountElement.textContent = data.count;
            cartCountElement.style.transform = 'scale(1.2)';
            setTimeout(() => {
                cartCountElement.style.transform = 'scale(1)';
            }, 200);
        }
    })
    .catch(error => console.error('Error updating cart count:', error));
}

function addButtonLoadingState(button, originalText) {
    button.textContent = 'Adding...';
    button.disabled = true;
    button.style.opacity = '0.7';
    
    return function removeLoadingState(success = true) {
        if (success) {
            button.textContent = 'Added!';
            button.style.backgroundColor = '#28a745';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.backgroundColor = '';
                button.disabled = false;
                button.style.opacity = '1';
            }, 1500);
        } else {
            button.textContent = originalText;
            button.disabled = false;
            button.style.opacity = '1';
        }
    };
}

function checkWishlistStatus(){
    document.querySelectorAll('.btn-wishlist').forEach(button => {
        const productId = button.dataset.productId;
        const productType = button.dataset.productType;

        if (productId && productType) {
            fetch('wishlist/check',{
                method : 'POST',
                headers: {
                    'Content-Type' : 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    product_id: productId,
                    product_type: productType
                })
            })
            .then(response => response.json())
            .then(data => {
                if(data.in_wishlist) {
                    button.classList.add('active');
                    button.style.background = '#ff4757';
                    button.style.color = 'white';
                    button.style.border = '2px solid #ff4757';
                    button.title = 'Remove from Wishlist'; 
                } else{
                    button.classList.remove('active');
                    button.style.background = '';
                    button.style.color = '';
                    button.style.border = '';
                    button.title = 'Add to Wishlist';
                }
            })  
            .catch(error => {
                console.error('Error checking wishlist status:', error);
            });
        }
    });
}

function removeFromWishlist(productId, productType, button){
    console.log('=== REMOVE FROME WISHLIST CALLED ===');
    console.log('Product ID:', productId);
    console.log('Product Type:', productType);

    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    const wishlistData = {
        product_id: productId,
        product_type: productType
    };

    fetch('/wishlist/remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(wishlistData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success){
            showNotification('Item removed from wishlist!', 'success');

            button.classList.remove('active');
            button.innerHTML = '<i class="fas fa-heart"></i>';
            button.style.background = '';
            button.style.color = '';
            button.style.border = '';
            button.title = 'Add to Wishlist';
            button.disabled = false;

            button.style.transform = 'scale(1.1)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 200);
        } else{
            showNotification(data.message || 'Failed to remove from wishlist', 'error');
            button.innerHTML = originalHTML;
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error removing from wishlist:', error);
        showNofitication('Error removing from wishlist', 'error');
        button.innerHTML = originalHTML;
        button.disabled = false;
    })
}

// ===========================================
// BUTTON INITIALIZATION
// ===========================================
function initializeCartButtons() {
    document.querySelectorAll('.btn-add-cart, .add-to-cart').forEach(button => {
        // Remove existing listeners to avoid duplicates
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent event bubbling to parent elements
            
            const productId = parseInt(this.dataset.productId);
            const productType = this.dataset.productType;
            const productName = this.dataset.productName;
            const price = parseFloat(this.dataset.price);
            const imagePath = this.dataset.imagePath;
            
            // Get quantity (default to 1, or from product view input)
            const qtyInput = document.getElementById('product-qty');
            const quantity = qtyInput ? parseInt(qtyInput.value) : 1;
            
            addToCart(productId, productType, productName, price, imagePath, quantity, this);
        });
    });
}

function initializeWishlistButtons() {
    document.querySelectorAll('.btn-wishlist').forEach(button => {
        
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);       ;

        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const productId = parseInt(this.dataset.productId);
            const productType = this.dataset.productType;

            if(this.classList.contains('active')){
                removeFromWishlist(productId, productType, this);
            } else{
                addToWishlist(productId, productType, this);
            }
        });
    });

    setTimeout(checkWishlistStatus, 100);
}

// Reset stuck buttons periodically
function resetStuckButtons() {
    const stuckButtons = document.querySelectorAll('button[disabled]');
    stuckButtons.forEach(button => {
        if (button.textContent.includes('Adding...')) {
            console.log('Resetting stuck button:', button);
            button.disabled = false;
            button.textContent = 'ADD TO CART';
            button.style.opacity = '1';
        }
    });
}

setInterval(resetStuckButtons, 5000);

// Make functions globally available
window.addToCart = addToCart;
window.addToWishlist = addToWishlist;
window.updateCartCount = updateCartCount;
window.checkUserAuthentication = checkUserAuthentication;
window.showNotification = showNotification;
window.showLoginDialog = showLoginDialog;
window.initializeCartButtons = initializeCartButtons;
window.initializeWishlistButtons = initializeWishlistButtons;