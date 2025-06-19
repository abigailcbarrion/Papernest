document.addEventListener('DOMContentLoaded', function() {
    initializeCarousel();
    // Cart and wishlist initialization now handled by cart-utils.js
});

// Carousel functionality only
function initializeCarousel() {
    const carousel = document.getElementById('bookCarousel');
    let prevBtn = document.getElementById('prevBtn');
    let nextBtn = document.getElementById('nextBtn');
    if (!carousel) return;

    let isMobile = window.innerWidth <= 768;
    if (isMobile) {
        setupMobileCarousel(carousel, prevBtn, nextBtn);
    } else {
        setupDesktopCarousel(carousel, prevBtn, nextBtn);
    }

    // Track mode and re-initialize only when mode changes
    window.addEventListener('resize', function () {
        const newIsMobile = window.innerWidth <= 768;
        if (newIsMobile !== isMobile) {
            isMobile = newIsMobile;
            // Always get fresh references after clearing listeners
            prevBtn = document.getElementById('prevBtn');
            nextBtn = document.getElementById('nextBtn');
            if (isMobile) {
                setupMobileCarousel(carousel, prevBtn, nextBtn);
            } else {
                setupDesktopCarousel(carousel, prevBtn, nextBtn);
            }
        }
    });
}

function clearArrowListeners(prevBtn, nextBtn) {
    // Clone the node to remove all listeners
    if (prevBtn) {
        const newPrev = prevBtn.cloneNode(true);
        prevBtn.parentNode.replaceChild(newPrev, prevBtn);
    }
    if (nextBtn) {
        const newNext = nextBtn.cloneNode(true);
        nextBtn.parentNode.replaceChild(newNext, nextBtn);
    }
}

function setupMobileCarousel(carousel, prevBtn, nextBtn) {
    clearArrowListeners(prevBtn, nextBtn);
    prevBtn = document.getElementById('prevBtn');
    nextBtn = document.getElementById('nextBtn');

    if (prevBtn) prevBtn.style.display = 'flex';
    if (nextBtn) nextBtn.style.display = 'flex';

    // Track current card index for snap navigation
    let currentCardIndex = 0;

    const getCards = () => carousel.querySelectorAll('.product-card');
    
    const getCardPosition = (index) => {
        const cards = getCards();
        if (index >= cards.length) return carousel.scrollWidth - carousel.clientWidth;
        if (index < 0) return 0;
        
        const card = cards[index];
        return card.offsetLeft;
    };

    prevBtn?.addEventListener('click', function () {
        const cards = getCards();
        if (currentCardIndex > 0) {
            currentCardIndex--;
            const targetPosition = getCardPosition(currentCardIndex);
            carousel.scrollTo({
                left: targetPosition,
                behavior: 'smooth'
            });
        }
    });

    nextBtn?.addEventListener('click', function () {
        const cards = getCards();
        if (currentCardIndex < cards.length - 1) {
            currentCardIndex++;
            const targetPosition = getCardPosition(currentCardIndex);
            carousel.scrollTo({
                left: targetPosition,
                behavior: 'smooth'
            });
        }
    });

    // Update current index based on scroll position
    carousel.addEventListener('scroll', function() {
        const cards = getCards();
        const scrollLeft = carousel.scrollLeft;
        
        // Find the closest card to the left edge
        let closestIndex = 0;
        let minDistance = Math.abs(scrollLeft - getCardPosition(0));
        
        for (let i = 1; i < cards.length; i++) {
            const distance = Math.abs(scrollLeft - getCardPosition(i));
            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = i;
            }
        }
        
        currentCardIndex = closestIndex;
    });

    addScrollIndicators(carousel);
}

function setupDesktopCarousel(carousel, prevBtn, nextBtn) {
    clearArrowListeners(prevBtn, nextBtn);
    prevBtn = document.getElementById('prevBtn');
    nextBtn = document.getElementById('nextBtn');

    if (prevBtn) prevBtn.style.display = 'flex';
    if (nextBtn) nextBtn.style.display = 'flex';

    // Track current card index for snap navigation
    let currentCardIndex = 0;

    const getCards = () => carousel.querySelectorAll('.product-card');
    
    const getCardPosition = (index) => {
        const cards = getCards();
        if (index >= cards.length) return carousel.scrollWidth - carousel.clientWidth;
        if (index < 0) return 0;
        
        const card = cards[index];
        return card.offsetLeft;
    };

    prevBtn?.addEventListener('click', function () {
        const cards = getCards();
        if (currentCardIndex > 0) {
            currentCardIndex--;
            const targetPosition = getCardPosition(currentCardIndex);
            carousel.scrollTo({
                left: targetPosition,
                behavior: 'smooth'
            });
        }
    });

    nextBtn?.addEventListener('click', function () {
        const cards = getCards();
        if (currentCardIndex < cards.length - 1) {
            currentCardIndex++;
            const targetPosition = getCardPosition(currentCardIndex);
            carousel.scrollTo({
                left: targetPosition,
                behavior: 'smooth'
            });
        }
    });

    // Update current index based on scroll position
    carousel.addEventListener('scroll', function() {
        const cards = getCards();
        const scrollLeft = carousel.scrollLeft;
        
        // Find the closest card to the left edge
        let closestIndex = 0;
        let minDistance = Math.abs(scrollLeft - getCardPosition(0));
        
        for (let i = 1; i < cards.length; i++) {
            const distance = Math.abs(scrollLeft - getCardPosition(i));
            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = i;
            }
        }
        
        currentCardIndex = closestIndex;
    });

    addScrollIndicators(carousel);
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