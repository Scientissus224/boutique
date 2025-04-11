// ----------------------------------------- Gestion de la recherche principale -------------------------
// ----------------------------------------- Fonction pour charger la vidéo quand elle devient visible -------------------------

document.addEventListener("DOMContentLoaded", function() {
    const videos = document.querySelectorAll('.lazy-video');
    
    const lazyLoadVideo = (video) => {
        const source = video.querySelector('source');
        const videoSrc = source.getAttribute('data-src');
        source.setAttribute('src', videoSrc);
        video.load(); // Charge la vidéo
        video.play(); // Lance la lecture de la vidéo
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                lazyLoadVideo(entry.target);
                observer.unobserve(entry.target); // Arrête d'observer cette vidéo
            }
        });
    }, { threshold: 0.5 });

    // Observer chaque vidéo avec la classe 'lazy-video'
    videos.forEach(video => observer.observe(video));
});