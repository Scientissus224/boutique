$(document).ready(function() {
  // Clic sur les boutons de page
  $(document).on('click', '.page-btn', function() {
      var pageNumber = $(this).data('page');  // Récupère le numéro de page

      // Affiche le spinner de chargement
      $('#loading-spinner').css('display', 'flex');

      // Délai de 1 seconde avant de faire la requête AJAX
      setTimeout(function() {
          $.ajax({
              url: '',  // URL de la même page
              type: 'GET',
              data: {
                  'page': pageNumber  // Envoie le numéro de page dans la requête
              },
              success: function(response) {
                  console.log('Réponse AJAX:', response);  // Affiche la réponse dans la console

                  // Cache le spinner après 1 seconde
                  setTimeout(function() {
                      $('#loading-spinner').hide();

                      // Met à jour le contenu des boutiques
                      $('#boutiques-container').html(response.boutiques);

                      // Met à jour la pagination
                      $('.page-btn').removeClass('active');  // Supprime la classe active de toutes les pages
                      $('.page-btn[data-page="' + response.current_page + '"]').addClass('active');  // Ajoute la classe active à la page actuelle

                      // Met à jour les boutons de pagination
                      var paginationHtml = '';
                      response.page_range.forEach(function(page) {
                          paginationHtml += '<button class="page-btn ' + (page === response.current_page ? 'active' : '') + '" data-page="' + page + '">' + page + '</button>';
                      });
                      $('#pagination-container').html('<span>Page : </span>' + paginationHtml);

                      // Anime l'apparition du contenu
                      $('#boutiques-container').css('opacity', '0').animate({ opacity: 1 }, 500);
                  }, 1000); // Délai de 1 seconde avant de cacher le spinner
              },
              error: function(xhr, status, error) {
                  console.error('Erreur AJAX:', error);  // Affiche l'erreur dans la console
                  console.error('Détails:', xhr, status);  // Affiche les détails de l'erreur

                  // Cache le spinner en cas d'erreur
                  $('#loading-spinner').hide();

                  alert("Une erreur s'est produite.");
              }
          });
      }, 1000); // Délai de 1 seconde avant de lancer la requête AJAX
  });
});