
// Script de rechargement lors de la navigation avant/arrière
document.addEventListener('DOMContentLoaded', function() {
    // Détecte les événements de navigation (avant/arrière)
    window.addEventListener('popstate', function(event) {
        // Force le rechargement de la page
        window.location.reload(true);
    });

    // Pour certains navigateurs qui cachent le cache
    if (window.performance) {
        // Vérifie si la page a été chargée depuis le cache
        if (performance.navigation.type === 2) {
            // Type 2 = navigation via les boutons avant/arrière
            window.location.reload(true);
        }
    }
    
    // Solution alternative pour tous les navigateurs
    window.onpageshow = function(event) {
        if (event.persisted) {
            // La page a été chargée depuis le cache
            window.location.reload();
        }
    };
});
