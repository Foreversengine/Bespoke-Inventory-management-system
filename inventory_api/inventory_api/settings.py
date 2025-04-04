import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import os


# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security (Update for production!)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-here')  # Always use env var in prod
DEBUG = os.getenv('DEBUG', 'False') == 'True'  # False in production
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost 127.0.0.1').split()  # Add your domain in prod

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',  # For frontend API access
    
    # Local
    'inventory.apps.InventoryConfig',  # Your app
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS before other middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# DRF Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    )
}

# JWT Settings (customize as needed)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS (adjust for your frontend in production)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React/Vue dev server
    "http://127.0.0.1:3000",
]

# Database (PostgreSQL recommended for production)

load_dotenv()  # This loads the .env file


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('inventory_db'),
        'USER': os.getenv('inventory_user'),
        'PASSWORD': os.getenv('Demerisation1$'),
        'HOST': os.getenv('localhost'),
        'PORT': os.getenv('5432'),
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # For production

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'