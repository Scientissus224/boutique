from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
PORT = os.environ.get("PORT", 8000)

# Email settings (ensure email.py or environment variables are set)
from .email import *
EMAIL_BACKEND = EMAIL_BACKEND
EMAIL_USE_TLS = EMAIL_USE_TLS
EMAIL_HOST = EMAIL_HOST
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_PORT = EMAIL_PORT

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/table/'  
# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-9__p-#jd0*9ax7kudnc+%=jl9n)plo=y+v5lql+)pwlht$ooy0')

DEBUG = True



ALLOWED_HOSTS = [
    '10.5.50.71',        # Votre adresse IP Wi-Fi actuelle (peut changer)
    '127.0.0.1',         # Localhost
    'localhost',         # Alias pour 127.0.0.1
    '192.168.19.163',
    'warabaguinee.onrender.com',
]     


# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'shop.backends.UtilisateurBackend',
    'django.contrib.auth.backends.ModelBackend',  # Le backend par défaut
]
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # Limite de 10 Mo par fichier


# settings.py

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Assurez-vous que la session est stockée en base de données
SESSION_COOKIE_AGE = 14400  # Durée de vie des cookies de session (en secondes)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Pour que la session expire lorsque le navigateur se ferme


# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
    'boutique',
    'widget_tweaks',
    'cloudinary',
    'cloudinary_storage',

]


ROOT_URLCONF = 'boutique.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'boutique.wsgi.application'

# Base de données



DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'postgres://waraba_guinee_user:bsqpIXTODz1gtKX00aHj3PyqbcW7fvH1@dpg-cvspkd24d50c73d5ovh0-a.oregon-postgres.render.com/waraba_guinee')
    )
}

# Ajoutez manuellement les options de la connexion, si nécessaire
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}



# Validation du mot de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ['username', 'first_name', 'last_name']  # Ignorer 'email'
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Exige un minimum de 8 caractères
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Paramètres de localisation
LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Africa/Conakry'  # Ajustez selon votre besoin
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'  # URL pour accéder aux fichiers statiques

# Dossier où Django stocke les fichiers collectés (fichiers statiques collectés)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Dossier pour les fichiers statiques collectés

# Fichiers statiques supplémentaires pour les services comme Render
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Assurez-vous que vos fichiers sont dans le dossier 'static'
]

# Fichiers médias
MEDIA_URL = '/media/'  # URL pour accéder aux fichiers médias dans le navigateur
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Dossier où les fichiers uploadés sont enregistrés


# Configuration de Cloudinary---------------------
load_dotenv()  # Charge les variables d'environnement depuis .env

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}
# Spécifie le stockage des fichiers médias avec Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

#-------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
