<script>
  //-------------------------------- Responsive pour afficher la navbar------------------------------------------> 
function toggleMenu() {
    const search = document.querySelector('.navbar-search');
    const links = document.querySelector('.navbar-links');
    search.classList.toggle('show');
    links.classList.toggle('show');
}
  
//--------------------------------Gestion des sliders-----------------------------------------> 
/*--------------------Produits slider -----------------*/
let currentIndex = 0;

const slides = document.querySelectorAll('#slider1 .slide');
const dots = document.querySelectorAll('#slider1 .dot');
const totalSlides = slides.length; // Nombre total de slides

// Fonction pour afficher un slide spécifique
function showSlide(index) {
  if (index >= totalSlides) {
    currentIndex = 0;
  } else if (index < 0) {
    currentIndex = totalSlides - 1;
  } else {
    currentIndex = index;
  }

  slides.forEach((slide) => slide.classList.remove('active'));
  dots.forEach((dot) => dot.classList.remove('active'));

  slides[currentIndex].classList.add('active');
  dots[currentIndex].classList.add('active');

  document.querySelector('#slider1 .slides').style.transform = `translateX(-${currentIndex * 100}%)`;
}

function nextSlide() {
  showSlide(currentIndex + 1);
}

function prevSlide() {
  showSlide(currentIndex - 1);
}

dots.forEach((dot, index) => {
  dot.addEventListener('click', () => showSlide(index));
});

const autoSlideInterval = setInterval(nextSlide, 3000);

const slider = document.getElementById('slider1');
slider.addEventListener('mouseover', () => clearInterval(autoSlideInterval));
slider.addEventListener('mouseout', () => setInterval(nextSlide, 3000));

/*--------------------localisation slider -----------------*/
let currentIndexLocalization = 0;

const slidesLocalization = document.querySelectorAll('#localization-slider .slide');
const dotsLocalization = document.querySelectorAll('#localization-slider .dot');
const totalSlidesLocalization = slidesLocalization.length;

function showSlideLocalization(index) {
  if (index >= totalSlidesLocalization) {
    currentIndexLocalization = 0;
  } else if (index < 0) {
    currentIndexLocalization = totalSlidesLocalization - 1;
  } else {
    currentIndexLocalization = index;
  }

  slidesLocalization.forEach((slide) => slide.classList.remove('active'));
  dotsLocalization.forEach((dot) => dot.classList.remove('active'));

  slidesLocalization[currentIndexLocalization].classList.add('active');
  dotsLocalization[currentIndexLocalization].classList.add('active');

  document.querySelector('#localization-slider .slides').style.transform = `translateX(-${currentIndexLocalization * 100}%)`;
}

function nextSlideLocalization() {
  showSlideLocalization(currentIndexLocalization + 1);
}

function prevSlideLocalization() {
  showSlideLocalization(currentIndexLocalization - 1);
}

dotsLocalization.forEach((dot, index) => {
  dot.addEventListener('click', () => showSlideLocalization(index));
});

const autoSlideIntervalLocalization = setInterval(nextSlideLocalization, 3000);

const localizationSlider = document.getElementById('localization-slider');
localizationSlider.addEventListener('mouseover', () => clearInterval(autoSlideIntervalLocalization));
localizationSlider.addEventListener('mouseout', () => setInterval(nextSlideLocalization, 3000));

showSlideLocalization(currentIndexLocalization);

//<!-------------------------------- Gestion de la mise à jour du panier-----------------------------------------> 
document.addEventListener('DOMContentLoaded', function() {
  fetch('/obtenir-panier/')
    .then(response => response.json())
    .then(data => {
      const cartCount = document.querySelector('#cart-count');
      cartCount.textContent = data.total_articles;  // Mettez à jour le nombre d'articles dans le panier
    })
    .catch(error => {
      console.error('Erreur lors de la récupération du panier:', error);
    });

  // Ajout de l'écouteur d'événement sur le bouton de filtrage
  const applyFilterButton = document.getElementById('apply-filter-button');
  if (applyFilterButton) {
    applyFilterButton.addEventListener('click', performSearch);
  } else {
    console.error('Bouton "apply-filter-button" introuvable.');
  }
});

//<!-------------------------------- Modal de recherche de produit et filtrage Pour la recherche------------------------------------------> 
function openModal() {
  if (!document.getElementById('productModal').classList.contains('show')) {
    const modal = new bootstrap.Modal(document.getElementById('productModal'));
    modal.show();
  }
}

function performSearch(event) {
  event.preventDefault(); // Empêche le comportement par défaut du formulaire
  const searchQuery = document.getElementById('search-input-modal').value.trim();
  const minPrice = document.getElementById('min-price').value.trim();
  const maxPrice = document.getElementById('max-price').value.trim();

  if (searchQuery === "" && minPrice === "" && maxPrice === "") return;  // Ne pas faire de recherche sans critère

  const validMinPrice = minPrice !== "" ? minPrice : undefined;
  const validMaxPrice = maxPrice !== "" ? maxPrice : undefined;

  const userId = document.getElementById('user-data').getAttribute('data-user-id');

  $.ajax({
    url: `/recherche-produit/${userId}/`,
    data: {
      'nom': searchQuery,
      'prix_min': validMinPrice,
      'prix_max': validMaxPrice
    },
    success: function(response) {
      if (response.produits && response.produits.length > 0) {
        updateModalProducts(response.produits);
      } else {
        console.log('Aucun produit trouvé');
      }
    },
    error: function(error) {
      console.error('Erreur AJAX:', error);
    }
  });
}

function updateModalProducts(produits) {
  const productContainer = document.getElementById('product-container-modal');
  productContainer.innerHTML = '';

  if (produits.length > 0) {
    produits.forEach(product => {
      const productElement = createProductElement(product);
      const colDiv = document.createElement('div');
      colDiv.classList.add('col-6', 'col-lg-2', 'mb-4');
      colDiv.appendChild(productElement);
      productContainer.appendChild(colDiv);
    });
  } else {
    productContainer.innerHTML = '<p>Aucun produit trouvé</p>';
  }
}

function createProductElement(product) {
  const div = document.createElement('div');
  div.classList.add('product-item-modal');
  div.dataset.name = product.nom.toLowerCase();
  div.dataset.price = product.prix;

  div.innerHTML = `
    <img src="${product.image_url || ''}" alt="${product.nom}" class="product-image-modal">
    <div class="product-info-modal">
      <div class="product-name-modal">${product.nom}</div>
      <div class="product-price">${product.prix} ${product.devise}</div>
    </div>
    <a href="${product.url}" class="product-link">
      <div class="product-icon-eye">👁️</div>
    </a>
  `;
  return div;
}

// -------------------Gestion Commentaires---------------------------
$(document).ready(function() {
    const userId = document.getElementById('user-data').getAttribute('data-user-id');

  if (userId) {
      console.log('ID utilisateur récupéré :', userId);  // Log pour vérifier l'ID

      function chargerCommentaires() {
          $.ajax({
              url: '/recuperer_commentaires/' + userId + '/',
              type: 'GET',
              success: function(response) {
                  console.log('Réponse du serveur :', response);  // Log pour vérifier la réponse du serveur
                  if (response.success) {
                      let commentairesHTML = '';
                      response.commentaires.forEach(function(commentaire) {
                          commentairesHTML += `
                              <div class="commentaire">
                                  <div class="image-container">
                                      <img src="${commentaire.image_profil || 'https://via.placeholder.com/150'}" alt="Image produit" class="image-produit">
                                  </div>
                                  <div class="details">
                                      <p class="nom-client">${commentaire.nom_visiteur}</p>
                                      <p class="date-commentaire">${commentaire.date_commentaire}</p>
                                      <p class="texte-commentaire">${commentaire.commentaire}</p>
                                      <p class="etoiles">${'★'.repeat(commentaire.note)}${'☆'.repeat(5 - commentaire.note)}</p>
                                  </div>
                              </div>
                          `;
                      });
                      $('#commentaires-container').html(commentairesHTML);
                  } else {
                      console.log('Erreur lors de la récupération des commentaires:', response.message);
                  }
              },
              error: function(xhr, status, error) {
                  console.log('Erreur lors de la récupération des commentaires:', xhr, status, error);
              }
          });
      }

      chargerCommentaires();
  } else {
      console.log('Aucun ID utilisateur trouvé. Impossible de charger les commentaires.');
  }
});

// -------------------Ajout Commentaire---------------------------
$(function() { 
    // Récupération de l'ID utilisateur à partir du div avec un attribut 'data'
    const userId = document.getElementById('user-data').getAttribute('data-user-id');
    console.log('ID utilisateur récupéré :', userId);

    // Fonction pour récupérer le token CSRF
    function getCookie(name) {
        const cookies = document.cookie.split(';').map(c => c.trim());
        for (let cookie of cookies) {
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.slice(name.length + 1));
            }
        }
        return null;
    }

    const csrfToken = getCookie('csrftoken');
    console.log('Token CSRF récupéré :', csrfToken);

    // Gestion de la soumission du formulaire
    $("#comment-form").on('submit', function(event) {
        event.preventDefault(); // Bloquer la soumission par défaut
        console.log('Formulaire soumis.');

        const formData = new FormData(this);
        formData.append('utilisateur_id', userId);

        $.ajax({
            url: `/poster_commentaire/${userId}/`,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                console.log('Réponse AJAX reçue:', response);
                if (response.success) {
                    // Notification de succès
                    $('#notification-message').text('Merci pour votre commentaire!');
                    $('#notification').fadeIn(500).delay(5000).fadeOut(500);

                    // Réinitialiser le formulaire
                    $("#comment-form")[0].reset();

                    // Rafraîchir la page pour mettre à jour les commentaires
                    location.reload();
                } else {
                    console.log('Erreur dans la réponse:', response.message);
                    alert('Erreur : ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('Erreur AJAX:', xhr, status, error);
                alert('Erreur de requête AJAX : ' + error);
            }
        });
    });

    // Fermer la notification via le bouton "Fermer"
    $('#notification-close').on('click', function() {
        $('#notification').fadeOut(500);
    });
});

</script>
