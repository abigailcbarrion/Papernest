document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            loginError.style.display = 'none';
            
            const formData = new FormData(loginForm);
            
            fetch('/login', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Handle success
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    // Mobile login dropdown handling - UPDATED
    const loginToggle = document.getElementById('loginToggle');
    const loginDropdown = document.getElementById('loginDropdown');
    const mobileCloseBtn = document.getElementById('mobileCloseBtn');
    
    function closeLoginDropdown() {
        if (loginDropdown && loginDropdown.classList.contains('show')) {
            // Add closing class for animation
            loginDropdown.classList.add('closing');
            
            // Wait for animation to complete, then hide
            setTimeout(() => {
                loginDropdown.classList.remove('show');
                loginDropdown.classList.remove('closing');
                document.body.style.overflow = '';
            }, 300); // Match the CSS transition duration
        }
    }
    
    function openLoginDropdown() {
        if (loginDropdown) {
            loginDropdown.classList.remove('closing'); // Remove any closing state
            loginDropdown.classList.add('show');
            if (window.innerWidth <= 768) {
                document.body.style.overflow = 'hidden';
            }
        }
    }
    
    // Handle login toggle click
    if (loginToggle && loginDropdown) {
        loginToggle.addEventListener('click', function(e) {
            e.preventDefault();
            if (loginDropdown.classList.contains('show')) {
                closeLoginDropdown();
            } else {
                openLoginDropdown();
            }
        });
    }
    
    // Handle mobile close button click
    if (mobileCloseBtn) {
        mobileCloseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            closeLoginDropdown();
        });
    }
    
    // Close dropdown when clicking outside (but not on form elements)
    document.addEventListener('click', function(e) {
        if (loginDropdown && loginDropdown.classList.contains('show')) {
            // Don't close if clicking inside the dropdown content
            if (!loginDropdown.contains(e.target) && !loginToggle.contains(e.target)) {
                closeLoginDropdown();
            }
        }
    });
    
    // Prevent dropdown from closing when clicking inside it
    if (loginDropdown) {
        loginDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            document.body.style.overflow = '';
            if (loginDropdown) {
                loginDropdown.classList.remove('show');
                loginDropdown.classList.remove('closing');
            }
        }
    });
    
    // Handle escape key to close dropdown
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && loginDropdown && loginDropdown.classList.contains('show')) {
            closeLoginDropdown();
        }
    });

    // Mobile Navigation Handling - keep existing code
    const mobileNavToggle = document.getElementById('mobileNavToggle');
    const mobileNav = document.getElementById('mobileNav');
    const mobileNavClose = document.getElementById('mobileNavClose');
    const mobileNavOverlay = document.getElementById('mobileNavOverlay');
    
    function openMobileNav() {
        mobileNav.classList.add('show');
        mobileNavOverlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
    
    function closeMobileNav() {
        mobileNav.classList.remove('show');
        mobileNavOverlay.classList.remove('show');
        document.body.style.overflow = '';
        
        // Close all dropdowns
        document.querySelectorAll('.mobile-dropdown-content').forEach(dropdown => {
            dropdown.classList.remove('show');
        });
        document.querySelectorAll('.mobile-dropdown-btn').forEach(btn => {
            btn.classList.remove('active');
        });
    }
    
    // Toggle mobile nav
    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', function(e) {
            e.preventDefault();
            openMobileNav();
        });
    }
    
    // Close mobile nav
    if (mobileNavClose) {
        mobileNavClose.addEventListener('click', function(e) {
            e.preventDefault();
            closeMobileNav();
        });
    }
    
    // Close when clicking overlay
    if (mobileNavOverlay) {
        mobileNavOverlay.addEventListener('click', function() {
            closeMobileNav();
        });
    }
    
    // Handle mobile dropdown toggles
    document.querySelectorAll('.mobile-dropdown-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('data-target');
            const targetDropdown = document.getElementById(targetId);
            const isActive = this.classList.contains('active');
            
            // Close all other dropdowns
            document.querySelectorAll('.mobile-dropdown-content').forEach(dropdown => {
                dropdown.classList.remove('show');
            });
            document.querySelectorAll('.mobile-dropdown-btn').forEach(button => {
                button.classList.remove('active');
            });
            
            // Toggle current dropdown
            if (!isActive) {
                targetDropdown.classList.add('show');
                this.classList.add('active');
            }
        });
    });
    
    // Close mobile nav when clicking on links
    document.querySelectorAll('.mobile-nav-item, .mobile-dropdown-content a').forEach(link => {
        link.addEventListener('click', function() {
            closeMobileNav();
        });
    });
    
    // Handle escape key for mobile nav
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileNav && mobileNav.classList.contains('show')) {
            closeMobileNav();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileNav();
        }
    });
});
