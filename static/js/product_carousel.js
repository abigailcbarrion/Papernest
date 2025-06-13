// Product Carousel JavaScript - Mobile Responsive
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('bookCarousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (!carousel) return;
    
    // Mobile detection
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Mobile: Enable touch scrolling, hide arrows
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
        
        // Add momentum scrolling for iOS
        carousel.style.webkitOverflowScrolling = 'touch';
        
        // Optional: Add scroll indicators
        addScrollIndicators();
        
    } else {
        // Desktop: Use arrow navigation
        if (prevBtn && nextBtn) {
            setupDesktopCarousel();
        }
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const newIsMobile = window.innerWidth <= 768;
        
        if (newIsMobile && !isMobile) {
            // Switched to mobile
            if (prevBtn) prevBtn.style.display = 'none';
            if (nextBtn) nextBtn.style.display = 'none';
        } else if (!newIsMobile && isMobile) {
            // Switched to desktop
            if (prevBtn) prevBtn.style.display = 'flex';
            if (nextBtn) nextBtn.style.display = 'flex';
        }
    });
    
    function setupDesktopCarousel() {
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
    
    function addScrollIndicators() {
        // Add visual indicators for scrollable content
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
    
    // Add to cart functionality
    document.querySelectorAll('.btn-add-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Add loading state
            const originalText = this.textContent;
            this.textContent = 'Adding...';
            this.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                this.textContent = 'Added!';
                this.style.background = '#28a745';
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = '';
                    this.disabled = false;
                }, 1500);
            }, 500);
        });
    });
    
    // Wishlist functionality
    document.querySelectorAll('.btn-wishlist').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            this.classList.toggle('active');
            
            // Add animation feedback
            this.style.transform = 'scale(1.2)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
});