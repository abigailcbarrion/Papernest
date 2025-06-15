// Mobile-Responsive Carousel JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.carousel');
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.querySelector('.carousel-btn.prev');
    const nextBtn = document.querySelector('.carousel-btn.next');
    const dots = document.querySelectorAll('.dot');
    
    let currentSlide = 0;
    let isTransitioning = false;
    let autoPlayInterval;
    let touchStartX = 0;
    let touchEndX = 0;
    
    // Initialize carousel
    function init() {
        showSlide(0);
        setupEventListeners();
        startAutoPlay();
        lazyLoadImages();
    }
    
    // Show specific slide
    function showSlide(index) {
        if (isTransitioning) return;
        
        isTransitioning = true;
        
        dots.forEach(dot => dot.classList.remove('active'));
        dots[index].classList.add('active');
        
        carousel.style.transform = `translateX(-${index * 100}%)`;

        currentSlide = index;

        setTimeout(() => {
            isTransitioning = false;
        }, 500);
    }
    
    // Next slide
    function nextSlide() {
        const next = (currentSlide + 1) % slides.length;
        showSlide(next);
    }
    
    // Previous slide
    function prevSlide() {
        const prev = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(prev);
    }
    
    // Setup event listeners
    function setupEventListeners() {
        // Button clicks
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                nextSlide();
                resetAutoPlay();
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                prevSlide();
                resetAutoPlay();
            });
        }
        
        // Dot clicks
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                showSlide(index);
                resetAutoPlay();
            });
        });
        
        // Touch gestures for mobile
        if (carousel) {
            carousel.addEventListener('touchstart', handleTouchStart, { passive: true });
            carousel.addEventListener('touchmove', handleTouchMove, { passive: true });
            carousel.addEventListener('touchend', handleTouchEnd, { passive: true });
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                prevSlide();
                resetAutoPlay();
            } else if (e.key === 'ArrowRight') {
                nextSlide();
                resetAutoPlay();
            }
        });
        
        // Pause on hover (desktop)
        if (carousel) {
            carousel.addEventListener('mouseenter', pauseAutoPlay);
            carousel.addEventListener('mouseleave', startAutoPlay);
        }
        
        // Pause when page is not visible
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                pauseAutoPlay();
            } else {
                startAutoPlay();
            }
        });
    }
    
    // Touch event handlers
    function handleTouchStart(e) {
        touchStartX = e.touches[0].clientX;
        pauseAutoPlay();
    }
    
    function handleTouchMove(e) {
        // Optional: Add visual feedback during swipe
    }
    
    function handleTouchEnd(e) {
        touchEndX = e.changedTouches[0].clientX;
        handleSwipe();
        startAutoPlay();
    }
    
    // Handle swipe gesture
    function handleSwipe() {
        const swipeThreshold = 50; // Minimum distance for swipe
        const swipeDistance = touchStartX - touchEndX;
        
        if (Math.abs(swipeDistance) > swipeThreshold) {
            if (swipeDistance > 0) {
                // Swiped left - next slide
                nextSlide();
            } else {
                // Swiped right - previous slide
                prevSlide();
            }
        }
    }
    
    // Auto-play functionality
    function startAutoPlay() {
        pauseAutoPlay(); // Clear any existing interval
        autoPlayInterval = setInterval(nextSlide, 5000); // 5 seconds
    }
    
    function pauseAutoPlay() {
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
            autoPlayInterval = null;
        }
    }
    
    function resetAutoPlay() {
        pauseAutoPlay();
        startAutoPlay();
    }
    
    // Lazy load images
    function lazyLoadImages() {
        slides.forEach(slide => {
            const img = slide.querySelector('img');
            if (img && img.src) {
                img.addEventListener('load', () => {
                    img.classList.add('loaded');
                });
                
                // If image is already loaded
                if (img.complete) {
                    img.classList.add('loaded');
                }
            }
        });
    }
    
    // Handle window resize
    function handleResize() {
        // Recalculate positions if needed
        showSlide(currentSlide);
    }
    
    window.addEventListener('resize', debounce(handleResize, 250));
    
    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Initialize the carousel
    init();
});