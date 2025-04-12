document.addEventListener('DOMContentLoaded', function() {
    const slider = document.querySelector('.slider');
    const slides = document.querySelector('.slides');
    const slideItems = document.querySelectorAll('.slide');
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    const indicators = document.querySelectorAll('.indicator');
    
    let currentIndex = 0;
    const slideCount = slideItems.length;
    let isAnimating = false;
    
    // Initialisation
    function initSlider() {
        updateSlider();
        
        // Événements
        prevBtn.addEventListener('click', goToPrevSlide);
        nextBtn.addEventListener('click', goToNextSlide);
        
        indicators.forEach(indicator => {
            indicator.addEventListener('click', function() {
                const slideIndex = parseInt(this.getAttribute('data-slide'));
                goToSlide(slideIndex);
            });
        });
        
        // Auto-slide
        setInterval(goToNextSlide, 5000);
    }
    
    function goToPrevSlide() {
        if (isAnimating) return;
        currentIndex = (currentIndex - 1 + slideCount) % slideCount;
        updateSlider();
    }
    
    function goToNextSlide() {
        if (isAnimating) return;
        currentIndex = (currentIndex + 1) % slideCount;
        updateSlider();
    }
    
    function goToSlide(index) {
        if (isAnimating || index === currentIndex) return;
        currentIndex = index;
        updateSlider();
    }
    
    function updateSlider() {
        isAnimating = true;
        
        // Déplacer les slides
        slides.style.transform = `translateX(-${currentIndex * 100}%)`;
        
        // Mettre à jour les indicateurs
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentIndex);
        });
        
        // Mettre à jour les slides actives
        slideItems.forEach((slide, index) => {
            slide.classList.toggle('active', index === currentIndex);
        });
        
        // Réinitialiser le flag d'animation
        setTimeout(() => {
            isAnimating = false;
        }, 700);
    }
    
    // Démarrer le slider
    initSlider();
});