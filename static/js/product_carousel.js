document.addEventListener('DOMContentLoaded', function() {
    initializeCarousel();
    initializeCartButtons();
    initializeWishlistButtons();
});

// Carousel functionality
function initializeCarousel() {
    const carousel = document.getElementById('bookCarousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (!carousel) return;
    
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        setupMobileCarousel(carousel, prevBtn, nextBtn);
    } else {
        setupDesktopCarousel(carousel, prevBtn, nextBtn);
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const newIsMobile = window.innerWidth <= 768;
        
        if (newIsMobile !== isMobile) {
            if (newIsMobile) {
                setupMobileCarousel(carousel, prevBtn, nextBtn);
            } else {
                setupDesktopCarousel(carousel, prevBtn, nextBtn);
            }
        }
    });
}

function setupMobileCarousel(carousel, prevBtn, nextBtn) {
    // Mobile: Enable touch scrolling, hide arrows
    if (prevBtn) prevBtn.style.display = 'none';
    if (nextBtn) nextBtn.style.display = 'none';
    
    // Add momentum scrolling for iOS
    carousel.style.webkitOverflowScrolling = 'touch';
    
    addScrollIndicators(carousel);
}

function setupDesktopCarousel(carousel, prevBtn, nextBtn) {
    // Desktop: Use arrow navigation
    if (prevBtn) prevBtn.style.display = 'flex';
    if (nextBtn) nextBtn.style.display = 'flex';
    
    if (prevBtn && nextBtn) {
        const cardWidth = 220; // Approximate card width including gap
        let currentScroll = 0;
        
        prevBtn.addEventListener('click', function() {
            currentScroll = Math.max(0, currentScroll - cardWidth * 2);
            carousel.scrollTo({
                left: currentScroll,
                behavior: 'smooth'
            });
        });
        
        nextBtn.addEventListener('click', function() {
            const maxScroll = carousel.scrollWidth - carousel.clientWidth;
            currentScroll = Math.min(maxScroll, currentScroll + cardWidth * 2);
            carousel.scrollTo({
                left: currentScroll,
                behavior: 'smooth'
            });
        });
        
        // Update current scroll position on manual scroll
        carousel.addEventListener('scroll', function() {
            currentScroll = carousel.scrollLeft;
        });
    }
}

function addScrollIndicators(carousel) {
    const container = carousel.parentElement;
    
    carousel.addEventListener('scroll', function() {
        const scrollPercentage = carousel.scrollLeft / (carousel.scrollWidth - carousel.clientWidth);
        
        // Update fade effects based on scroll position
        if (scrollPercentage > 0) {
            container.classList.add('scrolled-start');
        } else {
            container.classList.remove('scrolled-start');
        }
        
        if (scrollPercentage < 1) {
            container.classList.add('scrolled-end');
        } else {
            container.classList.remove('scrolled-end');
        }
    });
}

// Cart functionality
function initializeCartButtons() {
    document.querySelectorAll('.btn-add-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = parseInt(this.dataset.productId);
            const productType = this.dataset.productType;
            const productName = this.dataset.productName;
            const price = parseFloat(this.dataset.price);
            const imagePath = this.dataset.imagePath;
            
            addToCart(productId, productType, productName, price, imagePath, this);
        });
    });
}

function initializeWishlistButtons() {
    document.querySelectorAll('.btn-wishlist').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = parseInt(this.dataset.productId);
            const productType = this.dataset.productType;
            
            addToWishlist(productId, productType, this);
        });
    });
}

// Function to get CSRF token
function getCSRFToken() {
    const token = document.querySelector('meta[name=csrf-token]');
    return token ? token.getAttribute('content') : null;
}

// Update the addToCart function
function addToCart(productId, productType, productName, price, imagePath, button) {
    console.log('=== ADD TO CART CALLED ===');
    console.log('Parameters:', {productId, productType, productName, price, imagePath});
    
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
                quantity: 1
            };
            
            console.log('Sending cart data:', cartData);
            
            // Get CSRF token
            const csrfToken = getCSRFToken();
            const headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            };
            
            // Add CSRF token if available
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
            
            fetch('/cart/add', {
                method: 'POST',
                headers: headers,
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
                
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return response.json();
                } else {
                    return response.text().then(text => {
                        console.error('Received non-JSON response:', text);
                        throw new Error('Server returned HTML instead of JSON');
                    });
                }
            })
            .then(data => {
                console.log('Success response:', data);
                
                if (data.success) {
                    showNotification('Product added to cart!', 'success');
                    updateCartCount();
                    removeLoadingState(true);
                } else {
                    showNotification(data.message || 'Failed to add to cart', 'error');
                    removeLoadingState(false);
                }
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
                showNotification('Error adding to cart: ' + error.message, 'error');
                removeLoadingState(false);
            });
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
            showLoginDialog();
        });
}

function addToWishlist(productId, productType, button) {
    // Check if user is logged in by making a request to the server
    checkUserAuthentication()
        .then(isLoggedIn => {
            if (!isLoggedIn) {
                showLoginDialog();
                return;
            }
            
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
                    
                    // Update wishlist button appearance
                    button.classList.add('active');
                    button.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        button.style.transform = 'scale(1)';
                    }, 200);
                } else {
                    showNotification(data.message || 'Failed to add to wishlist', 'error');
                }
            })
            .catch(error => {
                console.error('Error adding to wishlist:', error);
                showNotification('Error adding to wishlist', 'error');
            });
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
            showLoginDialog();
        });
}

// Authentication check function
function checkUserAuthentication() {
    return fetch('/auth/check', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => data.authenticated)
    .catch(() => false);
}

// Login dialog function
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

// Utility functions for cart operations
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s;
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

function updateCartCount() {
    fetch('/cart/count', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement && data.count !== undefined) {
            cartCountElement.textContent = data.count;
            
            // Add animation to show the count updated
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
            button.style.background = '#28a745';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '';
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

// Export functions for global use
window.showNotification = showNotification;
window.updateCartCount = updateCartCount;
window.addButtonLoadingState = addButtonLoadingState;