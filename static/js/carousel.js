// Mobile-Responsive Carousel JavaScript - FIXED
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
    let autoPlayDelay = 3000; // 4 seconds - customizable
    let isAutoPlayEnabled = true; // Can be toggled
    let isPaused = false;
    
    // Check if we're on mobile
    function isMobile() {
        return window.innerWidth <= 768;
    }
    
    // Initialize carousel
    function init() {
        showSlide(0);
        setupEventListeners();
        startAutoPlay();
        lazyLoadImages();
    }
    
    // Show specific slide - FIXED to handle both desktop and mobile
    function showSlide(index) {
        if (isTransitioning) return;
        
        isTransitioning = true;
        
        // Update dots
        dots.forEach(dot => dot.classList.remove('active'));
        if (dots[index]) {
            dots[index].classList.add('active');
        }
        
        if (isMobile()) {
            // Mobile approach: use classes for individual slides
            slides.forEach((slide, i) => {
                slide.classList.remove('active', 'prev');
                
                if (i === index) {
                    slide.classList.add('active');
                } else if (i === index - 1 || (index === 0 && i === slides.length - 1)) {
                    slide.classList.add('prev');
                }
            });
        } else {
            // Desktop approach: transform the entire carousel
            carousel.style.transform = `translateX(-${index * 100}%)`;
        }

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
        
        // Pause on hover (desktop) - ENHANCED
        if (carousel) {
            carousel.addEventListener('mouseenter', () => {
                pauseAutoPlay();
            });
            carousel.addEventListener('mouseleave', () => {
                resumeAutoPlay();
            });
        }
        
        // Pause when page is not visible - ENHANCED
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                pauseAutoPlay();
            } else {
                resumeAutoPlay();
            }
        });
        
        // Pause when window loses focus
        window.addEventListener('blur', pauseAutoPlay);
        window.addEventListener('focus', resumeAutoPlay);
        
        // Handle window resize - IMPORTANT for responsive behavior
        window.addEventListener('resize', debounce(() => {
            handleResize();
        }, 250));
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
        resumeAutoPlay(); // Resume instead of start
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
    
    // Auto-play functionality - ENHANCED
    function startAutoPlay() {
        if (!isAutoPlayEnabled) return;
        
        pauseAutoPlay(); // Clear any existing interval
        isPaused = false;
        
        autoPlayInterval = setInterval(() => {
            if (!isPaused && !isTransitioning) {
                nextSlide();
            }
        }, autoPlayDelay);
    }
    
    function pauseAutoPlay() {
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
            autoPlayInterval = null;
        }
        isPaused = true;
    }
    
    function resumeAutoPlay() {
        if (isAutoPlayEnabled) {
            startAutoPlay();
        }
    }
    
    function resetAutoPlay() {
        pauseAutoPlay();
        setTimeout(() => {
            startAutoPlay();
        }, 100); // Small delay to prevent rapid resets
    }
    
    // Toggle auto-play on/off
    function toggleAutoPlay() {
        isAutoPlayEnabled = !isAutoPlayEnabled;
        if (isAutoPlayEnabled) {
            startAutoPlay();
        } else {
            pauseAutoPlay();
        }
        return isAutoPlayEnabled;
    }
    
    // Set custom auto-play delay
    function setAutoPlayDelay(delay) {
        autoPlayDelay = delay;
        if (isAutoPlayEnabled) {
            resetAutoPlay();
        }
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
    
    // Handle window resize - FIXED to reinitialize on resize
    function handleResize() {
        // Reset transforms and classes when switching between mobile/desktop
        if (isMobile()) {
            // Reset desktop transforms
            carousel.style.transform = '';
            // Apply mobile classes
            showSlide(currentSlide);
        } else {
            // Remove mobile classes
            slides.forEach(slide => {
                slide.classList.remove('active', 'prev');
            });
            // Apply desktop transform
            carousel.style.transform = `translateX(-${currentSlide * 100}%)`;
        }
    }
    
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
    
    // Expose public methods for external control (optional)
    window.carouselController = {
        nextSlide: nextSlide,
        prevSlide: prevSlide,
        goToSlide: showSlide,
        toggleAutoPlay: toggleAutoPlay,
        setAutoPlayDelay: setAutoPlayDelay,
        pauseAutoPlay: pauseAutoPlay,
        resumeAutoPlay: resumeAutoPlay,
        getCurrentSlide: () => currentSlide,
        getTotalSlides: () => slides.length,
        isAutoPlayEnabled: () => isAutoPlayEnabled
    };
});