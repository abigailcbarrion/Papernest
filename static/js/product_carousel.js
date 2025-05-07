document.addEventListener('DOMContentLoaded', function() {
    // Get carousel elements
    const carousel = document.getElementById('bookCarousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (!carousel || !prevBtn || !nextBtn) return;
    
    let scrollAmount = 0;
    const cardWidth = 240; // Card width + gap
    const visibleCards = Math.floor(carousel.offsetWidth / cardWidth);
    
    // Next button click event
    nextBtn.addEventListener('click', function() {
        const maxScroll = carousel.scrollWidth - carousel.offsetWidth;
        scrollAmount = Math.min(scrollAmount + cardWidth * Math.max(1, Math.floor(visibleCards / 2)), maxScroll);
        carousel.style.transform = `translateX(-${scrollAmount}px)`;
    });
    
    // Previous button click event
    prevBtn.addEventListener('click', function() {
        scrollAmount = Math.max(scrollAmount - cardWidth * Math.max(1, Math.floor(visibleCards / 2)), 0);
        carousel.style.transform = `translateX(-${scrollAmount}px)`;
    });
    
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
                this.style.backgroundColor = '#3498db';
            }, 1500);
        });
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        // Reset scroll when window is resized
        scrollAmount = 0;
        carousel.style.transform = `translateX(0)`;
    });
});