from pathlib import Path
import os
import cloudinary

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

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
    'warabaguinee-l9ax.onrender.com'
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'waraba_guinee_6px2',
        'USER': 'waraba_guinee_6px2_user',
        'PASSWORD': 'k6c3wS4HQtK97tnLjklh3N5CWHJEi9nv',
        'HOST': 'dpg-cvtq4eje5dus73adbpm0-a.oregon-postgres.render.com',
        'PORT': '5432',  # PostgreSQL utilise le port 5432 par défaut
    }
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

# Paramètres pour les fichiers statiques
STATIC_URL = '/static/'

# Dossier où seront collectés les fichiers statiques
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Répertoires supplémentaires pour les fichiers statiques
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# Fichiers médias
MEDIA_URL = '/media/'  # Le slash avant est nécessaire pour le bon fonctionnement
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 
# Répertoire où sont stockés les fichiers médias 
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dgbbbmmlm',
    'API_KEY': '341176238122211',
    'API_SECRET': 'lE0kq_OIv1wSv6Ul2TzP01s1RXI',
}

cloudinary.config( 
  cloud_name = "dgbbbmmlm", 
  api_key = "341176238122211", 
  api_secret = "lE0kq_OIv1wSv6Ul2TzP01s1RXI" 
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
