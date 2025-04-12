 // Gestion du thème et de l'icône
 document.addEventListener('DOMContentLoaded', function() {
    const themeIcon = document.getElementById('theme-toggle-desktop');
    const iconElement = themeIcon.querySelector('i');
    
    // Fonction pour mettre à jour l'icône
    function updateThemeIcon(isDark) {
        if (isDark) {
            iconElement.classList.remove('fa-sun');
            iconElement.classList.add('fa-moon');
        } else {
            iconElement.classList.remove('fa-moon');
            iconElement.classList.add('fa-sun');
        }
    }

    // Vérifier le thème initial
    const isDarkTheme = document.documentElement.getAttribute('data-theme') === 'dark';
    updateThemeIcon(isDarkTheme);

    // Écouter les changements de thème
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'data-theme') {
                const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
                updateThemeIcon(isDark);
            }
        });
    });

    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });
});