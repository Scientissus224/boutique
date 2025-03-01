document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    const searchContainer = document.querySelector('.search-container');
    const searchToggle = document.querySelector('.search-toggle');
    const userMenu = document.querySelector('.user-menu');
    const userIcon = document.querySelector('.user-icon');

    // Toggle menu hamburger
    hamburger.addEventListener('click', function() {
        this.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    // Toggle recherche sur mobile
    if (searchToggle) {
        searchToggle.addEventListener('click', function() {
            searchContainer.classList.toggle('active');
        });
    }

    // Fermer le menu au clic en dehors
    document.addEventListener('click', function(e) {
        if (!navLinks.contains(e.target) && !hamburger.contains(e.target)) {
            navLinks.classList.remove('active');
            hamburger.classList.remove('active');
        }

        if (!searchContainer.contains(e.target) && !searchToggle?.contains(e.target)) {
            searchContainer.classList.remove('active');
        }
    });

    // Gestion du menu utilisateur sur mobile
    if (userIcon) {
        userIcon.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                userMenu.classList.toggle('active');
            }
        });
    }

    // Fermer les menus au redimensionnement
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            navLinks.classList.remove('active');
            hamburger.classList.remove('active');
            searchContainer.classList.remove('active');
            userMenu.classList.remove('active');
        }
    });
}); 