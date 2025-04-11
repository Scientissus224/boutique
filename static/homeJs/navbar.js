  // -----------------------Gestion du menu mobile bouton humburger et la renitialisation du panier-------------------------------------------
   // Animation de la barre de recherche
const searchInput = document.querySelector('.search-input-nav');
const searchWrapper = document.querySelector('.search-wrapper');

searchInput.addEventListener('focus', () => {
  searchWrapper.classList.add('focused');
});

searchInput.addEventListener('blur', () => {
  searchWrapper.classList.remove('focused');
});

// Effet de survol sur les liens
document.querySelectorAll('.nav-links').forEach(link => {
  link.addEventListener('mouseenter', (e) => {
    const { left, top, width, height } = e.target.getBoundingClientRect();
    const ripple = document.createElement('div');
    ripple.classList.add('nav-link-ripple');
    ripple.style.left = `${left}px`;
    ripple.style.top = `${top}px`;
    ripple.style.width = `${width}px`;
    ripple.style.height = `${height}px`;
    document.body.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 1000);
  });
});

// Animation de la navbar au scroll
let lastScroll = 0;
const scrollThreshold = 100; // Seuil de défilement pour l'effet

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;
  
  // Ajouter/retirer la classe scrolled pour l'effet de fond
  if (currentScroll > scrollThreshold) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
  
  // Animation de masquage/affichage de la navbar
  if (currentScroll > lastScroll && currentScroll > 150 && !navMenu.classList.contains('show')) {
    // Scroll vers le bas - cacher la navbar
    navbar.style.transform = 'translateY(-100%)';
  } else {
    // Scroll vers le haut - montrer la navbar
    navbar.style.transform = 'translateY(0)';
  }
  
  lastScroll = currentScroll;
});

// Gestion du menu mobile
const hamburgerBtn = document.querySelector('.hamburger-btn');
const navMenu = document.querySelector('.nav-menu');
const navbar = document.querySelector('.navbar');

function toggleMenu() {
  navMenu.classList.toggle('show');
  navbar.classList.toggle('menu-open');
  
  // Animation de l'icône hamburger
  const hamburgerIcon = hamburgerBtn.querySelector('i');
  if (navMenu.classList.contains('show')) {
    hamburgerIcon.classList.remove('fa-bars');
    hamburgerIcon.classList.add('fa-times');
  } else {
    hamburgerIcon.classList.add('fa-bars');
    hamburgerIcon.classList.remove('fa-times');
  }
}

// Attacher l'événement au bouton hamburger
hamburgerBtn.addEventListener('click', toggleMenu);

// Fermer le menu mobile lors du clic sur un lien
document.querySelectorAll('.nav-links').forEach(link => {
  link.addEventListener('click', () => {
    if (navMenu.classList.contains('show')) {
      toggleMenu();
    }
  });
});
    //------------------------------Réinitialisation du panier-----------------------------------------
$(document).ready(function() {
    // Réinitialiser le panier quand la page se charge
    reinitialiserPanier();
});

function getCSRFToken() {
    return $('meta[name="csrf-token"]').attr('content');
}

function reinitialiserPanier() {
    $.ajax({
        url: '/reinitialiser-panier/',  // URL de la vue Django
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()  // Ajoute le token CSRF
        },
        success: function(response) {
           
            $('#panier').html('Total des articles : ' + response.total_articles);
        },
        error: function(xhr, status, error) {
            // Affiche une erreur si l'appel AJAX échoue
            const errorMessage = xhr.responseJSON ? xhr.responseJSON.message : 'Erreur inconnue';
            // L'alerte est supprimée, pas d'affichage du message d'alerte
        }
    });
}