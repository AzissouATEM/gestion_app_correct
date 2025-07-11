import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Charge les variables du .env local (en dev uniquement)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Sécurité
SECRET_KEY = os.getenv('SECRET_KEY', 'insecure-default-key')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

# 🔐 En prod, Render ajoute une variable RENDER_EXTERNAL_HOSTNAME
ALLOWED_HOSTS = [os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')]

# 🧩 Apps Django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # ton app principale
]

# 🧱 Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestion_app.urls'

# 📁 Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core', 'templates')],
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

WSGI_APPLICATION = 'gestion_app.wsgi.application'

# 📦 Base de données (Render injecte DATABASE_URL)
DATABASES = {
    'default': dj_database_url.config(
        default='mysql://user:password@localhost:3306/gestion_db',  # pour le local
        conn_max_age=600,
        ssl_require=False
    )
}

# 🔑 Auth personnalisé
AUTH_USER_MODEL = 'core.User'

# 🔐 Redirections login/logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# 🌍 Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 📁 Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
