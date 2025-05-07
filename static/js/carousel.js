document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.carousel');
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    let currentIndex = 0;
    
    // Function to update slide position
    function updateSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        slides[index].classList.add('active');
        dots[index].classList.add('active');
        
        currentIndex = index;
    }
    
    // Previous button click
    prevBtn.addEventListener('click', function() {
        let index = currentIndex - 1;
        if (index < 0) index = slides.length - 1;
        updateSlide(index);
    });
    
    // Next button click
    nextBtn.addEventListener('click', function() {
        let index = currentIndex + 1;
        if (index >= slides.length) index = 0;
        updateSlide(index);
    });
    
    // Dot click handlers
    dots.forEach(dot => {
        dot.addEventListener('click', function() {
            let index = parseInt(this.getAttribute('data-index'));
            updateSlide(index);
        });
    });
    
    // Auto slide every 5 seconds
    setInterval(function() {
        let index = currentIndex + 1;
        if (index >= slides.length) index = 0;
        updateSlide(index);
    }, 5000);
});