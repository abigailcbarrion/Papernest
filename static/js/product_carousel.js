document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('bookCarousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (!carousel || !prevBtn || !nextBtn) return;
    
    const cards = carousel.querySelectorAll('.product-card');
    if (cards.length === 0) return;
    
    const cardWidth = 220; // Width of each card
    const cardGap = 20;    // Gap between cards
    const totalCardWidth = cardWidth + cardGap;
    const visibleCards = 5;
    
    let currentPosition = 0;
    const maxPosition = Math.max(0, cards.length - visibleCards);
    
    // Update arrow visibility
    function updateArrows() {
        prevBtn.style.opacity = currentPosition <= 0 ? '0.3' : '0.7';
        prevBtn.style.pointerEvents = currentPosition <= 0 ? 'none' : 'auto';
        
        nextBtn.style.opacity = currentPosition >= maxPosition ? '0.3' : '0.7';
        nextBtn.style.pointerEvents = currentPosition >= maxPosition ? 'none' : 'auto';
    }
    
    // Move carousel by one card
    nextBtn.addEventListener('click', function() {
        if (currentPosition < maxPosition) {
            currentPosition++;
            carousel.style.transform = `translateX(-${currentPosition * totalCardWidth}px)`;
            updateArrows();
        }
    });
    
    prevBtn.addEventListener('click', function() {
        if (currentPosition > 0) {
            currentPosition--;
            carousel.style.transform = `translateX(-${currentPosition * totalCardWidth}px)`;
            updateArrows();
        }
    });
    
    // Initialize
    updateArrows();

    // Add to Cart buttons
    const addToCartButtons = document.querySelectorAll('.btn-add-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productCard = this.closest('.product-card');
            const productTitle = productCard.querySelector('.product-title').textContent;
            
            // You can add your cart logic here
            console.log(`Added to cart: ${productTitle}`);
            
            // Animation for feedback
            this.textContent = 'Added!';
            this.style.backgroundColor = '#27ae60';
            
            setTimeout(() => {
                this.textContent = 'Add to Cart';
                this.style.backgroundColor = '#11B8CE';
            }, 1500);
        });
    });
    
    // Wishlist button functionality
    const wishlistButtons = document.querySelectorAll('.btn-wishlist');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('active');
            const productCard = this.closest('.product-card');
            const productTitle = productCard.querySelector('.product-title').textContent;
            
            if (this.classList.contains('active')) {
                console.log(`Added to wishlist: ${productTitle}`);
            } else {
                console.log(`Removed from wishlist: ${productTitle}`);
            }
        });
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        // Reset position on resize
        currentPosition = 0;
        carousel.style.transform = `translateX(0)`;
        updateArrows();
    });
});