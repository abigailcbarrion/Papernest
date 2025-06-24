/**
 * Account page JavaScript functionality
 * Handles tab navigation, order viewing, and image error handling
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Account page loaded");
    
    // Check localStorage flag first
    const showOrdersTab = localStorage.getItem('showOrdersTab');
    if (showOrdersTab === 'true') {
        console.log("Found showOrdersTab flag in localStorage");
        localStorage.removeItem('showOrdersTab');
        showSection('orders');
        return;
    }
    
    // Then check URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const sectionParam = urlParams.get('section');
    
    if (sectionParam && ['dashboard', 'orders', 'discount', 'wishlist'].includes(sectionParam)) {
        showSection(sectionParam);
    } else {
        // Default to dashboard
        showSection('dashboard');
    }
    
    // Fix image errors
    document.querySelectorAll('img').forEach(img => {
        img.onerror = function() {
            if (!this.src.includes('placeholder.png')) {
                this.src = '/static/images/placeholder.png';
            }
        };
    });
});

// Simple section switching function
function showSection(sectionName) {
    console.log('Showing section:', sectionName);
    
    // Hide all containers
    document.getElementById('dashboard-container').style.display = 'none';
    document.getElementById('orders-container').style.display = 'none';
    document.getElementById('discount-container').style.display = 'none';
    document.getElementById('wishlist-container').style.display = 'none';
    
    // Remove active class from all nav items
    document.querySelectorAll('.account-nav h4').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show the selected section and activate nav item
    switch(sectionName) {
        case 'orders':
            document.getElementById('orders-container').style.display = 'block';
            document.getElementById('nav-orders').classList.add('active');
            break;
        case 'discount':
            document.getElementById('discount-container').style.display = 'block';
            document.getElementById('nav-discount').classList.add('active');
            break;
        case 'wishlist':
            document.getElementById('wishlist-container').style.display = 'block';
            document.getElementById('nav-wishlist').classList.add('active');
            break;
        default:
            document.getElementById('dashboard-container').style.display = 'block';
            document.getElementById('nav-dashboard').classList.add('active');
    }
    
    // Update URL
    const url = new URL(window.location);
    url.searchParams.set('section', sectionName);
    window.history.pushState({}, '', url);
}

// Simple function to remove from wishlist
function removeFromWishlist(productId, productType, button) {
    if (!confirm('Are you sure you want to remove this item from your wishlist?')) {
        return;
    }
    
    fetch('/remove-from-wishlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            product_id: productId,
            product_type: productType
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Remove the item from the DOM
            const item = button.closest('.wishlist-item');
            if (item) {
                item.remove();
            }
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Account popup functions
function showEditPopup() {
    document.getElementById('editDetailsPopup').style.display = 'flex';
}

function closeEditPopup() {
    document.getElementById('editDetailsPopup').style.display = 'none';
}

function showChangePasswordPopup() {
    document.querySelector('.change-password-overlay').style.display = 'flex';
}

function closeChangePasswordPopup() {
    document.querySelector('.change-password-overlay').style.display = 'none';
}

function openAddressPopup() {
    document.getElementById('addressPopup').style.display = 'flex';
}

function closeAddressPopup() {
    document.getElementById('addressPopup').style.display = 'none';
}

function showEditAddress() {
    closeAddressPopup();
    document.getElementById('editAddressPopup').style.display = 'flex';
}

function closeEditAddressPopup() {
    document.getElementById('editAddressPopup').style.display = 'none';
}

function confirmDeleteAddress() {
    closeAddressPopup();
    document.getElementById('deleteAddressPopup').style.display = 'flex';
}

function closeDeleteAddressPopup() {
    document.getElementById('deleteAddressPopup').style.display = 'none';
}

function togglePassword(button) {
    const input = button.previousElementSibling;
    if (input.type === 'password') {
        input.type = 'text';
        button.classList.add('showing');
    } else {
        input.type = 'password';
        button.classList.remove('showing');
    }
}