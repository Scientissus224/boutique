 # Définition de la constante pour le HTML de la navbar
NAVBAR_HTML = '''
    <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">Ma Boutique</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" 
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="#">Produits</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Localisation</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Commentaires</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Contact</a></li>
                </ul>
                <form class="d-flex me-auto">
                    <input class="form-control me-2" type="search" placeholder="Recherche" aria-label="Search">
                </form>
                <a href="#" class="btn">
                    <i class="bi bi-cart-fill fs-4"></i>
                </a>
            </div>
        </div>
    </nav>
    '''
SLIDER_HTML = '''
<div class="container product-slider">
    <div id="productCarousel" class="carousel slide" data-bs-ride="carousel">
        <div class="carousel-inner">
            {% for slider in sliders %}
                <div class="carousel-item {% if forloop.first %}active{% endif %}">
                    {% if slider.image %}
                        <img src="{{ slider.image.url }}" class="d-block w-100" alt="{{ slider.title }}">
                    {% else %}
                        <img src="https://via.placeholder.com/1200x400.png?text=Image+non+disponible" class="d-block w-100" alt="Image non disponible">
                    {% endif %}
                    <div class="carousel-caption d-none d-md-block">
                        {% if slider.title %}
                            <h5>{{ slider.title }}</h5>
                        {% endif %}
                        {% if slider.description %}
                            <p>{{ slider.description }}</p>
                        {% endif %}
                    </div>
                </div>
            {% empty %}
                <div class="carousel-item active">
                    <img src="https://via.placeholder.com/1200x400.png?text=Aucun+Slider" class="d-block w-100" alt="Aucun Slider">
                    <div class="carousel-caption d-none d-md-block">
                        <h5>Aucun Slider Disponible</h5>
                        <p>Il n'y a actuellement aucun slider disponible pour votre compte.</p>
                    </div>
                </div>
            {% endfor %}
        </div>
        <button class="carousel-control-prev" type="button" data-bs-target="#productCarousel" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Précédent</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#productCarousel" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Suivant</span>
        </button>
    </div>
</div>
'''
FOOTER_HTML = '''
    <footer class="bg-dark text-white py-5">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <h5>À propos</h5>
                    <ul class="list-unstyled">
                        <li><a href="#" class="text-white">Notre histoire</a></li>
                        <li><a href="#" class="text-white">Politique de confidentialité</a></li>
                        <li><a href="#" class="text-white">Mentions légales</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>Service client</h5>
                    <ul class="list-unstyled">
                        <li><a href="#" class="text-white">Contact</a></li>
                        <li><a href="#" class="text-white">Retours et échanges</a></li>
                        <li><a href="#" class="text-white">FAQ</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>Suivez-nous</h5>
                    <ul class="list-unstyled">
                        <li><a href="#" class="text-white"><i class="fab fa-facebook"></i> Facebook</a></li>
                        <li><a href="#" class="text-white"><i class="fab fa-instagram"></i> Instagram</a></li>
                        <li><a href="#" class="text-white"><i class="fab fa-twitter"></i> Twitter</a></li>
                    </ul>
                </div>
            </div>
            <div class="row mt-4">
                <div class="col-12 text-center">
                    <p>&copy; 2024 Ma Boutique. Tous droits réservés.</p>
                </div>
            </div>
        </div>
    </footer>
'''
