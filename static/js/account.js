
document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.account-nav h4');
    const accountContainer = document.querySelector('.account-container');
    const ordersContainer = document.querySelector('.orders-container');
    const discountCardsContainer = document.querySelector('.discount-cards-container');
    const wishlistContainer = document.querySelector('.my-wishlist-container');

    // Check if we should show wishlist section based on URL or page variable
    const currentPath = window.location.pathname;
    const activeSection = '{{ active_section }}'; // Get from template variable
    
    function showSection(sectionName) {
        // Hide all sections
        accountContainer.style.display = 'none';
        if (ordersContainer) ordersContainer.style.display = 'none';
        if (discountCardsContainer) discountCardsContainer.style.display = 'none';
        if (wishlistContainer) wishlistContainer.style.display = 'none';
        
        // Remove active class from all nav items
        navItems.forEach(i => i.classList.remove('active'));
        
        // Show the requested section
        switch(sectionName) {
            case 'wishlist':
                if (wishlistContainer) {
                    wishlistContainer.style.display = 'block';
                    // Find and activate the wishlist nav item
                    navItems.forEach(item => {
                        if (item.textContent.trim() === 'My Wishlist') {
                            item.classList.add('active');
                        }
                    });
                }
                break;
            case 'orders':
                if (ordersContainer) {
                    ordersContainer.style.display = 'block';
                    navItems.forEach(item => {
                        if (item.textContent.trim() === 'My Orders') {
                            item.classList.add('active');
                        }
                    });
                }
                break;
            case 'discount-cards':
                if (discountCardsContainer) {
                    discountCardsContainer.style.display = 'block';
                    navItems.forEach(item => {
                        if (item.textContent.trim() === 'Discount Cards') {
                            item.classList.add('active');
                        }
                    });
                }
                break;
            default:
                accountContainer.style.display = 'block';
                navItems.forEach(item => {
                    if (item.textContent.trim() === 'Dashboard') {
                        item.classList.add('active');
                    }
                });
        }
    }
    
    // Initialize based on URL or active section
    if (currentPath.includes('/wishlist') || activeSection === 'wishlist') {
        showSection('wishlist');
    } else {
        showSection('dashboard');
    }

    navItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const sectionName = this.textContent.trim();
            
            if (sectionName === 'Dashboard') {
                showSection('dashboard');
            } else if (sectionName === 'My Orders') {
                showSection('orders');
            } else if (sectionName === 'Discount Cards') {
                showSection('discount-cards');
            } else if (sectionName === 'My Wishlist') {
                showSection('wishlist');
            }
        });
    });
});
