document.addEventListener('DOMContentLoaded', function() {
    initializeCarousel();
    // Cart and wishlist initialization now handled by cart-utils.js
});

// Carousel functionality only
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