"""
Production Django settings for allinonenepal project.
Extends base.py with production-specific settings.
"""

import os
from urllib.parse import unquote, urlparse
from .base import *

# Add Cloudinary apps for production storage
INSTALLED_APPS.insert(INSTALLED_APPS.index('django.contrib.staticfiles'), 'cloudinary_storage')
INSTALLED_APPS.append('cloudinary')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database - PostgreSQL for production
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    parsed_url = urlparse(DATABASE_URL)
    db_name = unquote(parsed_url.path[1:]) if parsed_url.path else ''
    db_user = unquote(parsed_url.username) if parsed_url.username else ''
    db_password = unquote(parsed_url.password) if parsed_url.password else ''
    db_host = parsed_url.hostname or ''
    db_port = parsed_url.port or ''

    db_options = {}
    db_sslmode = os.getenv('DB_SSLMODE')
    if db_sslmode:
        db_options['sslmode'] = db_sslmode

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': db_port,
            'CONN_MAX_AGE': 60,  # Keep connections alive for 60 seconds
            'CONN_HEALTH_CHECKS': True, # Check if connection is alive before using
        }
    }
    if db_options:
        DATABASES['default']['OPTIONS'] = db_options
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'allinonenepal_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }

# Security Settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}

# HTTPS Settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email Backend - SMTP for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@allinonenepal.com')

# Email provider selection for API-based email services
EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'resend')

# CORS - Strict in production
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'https://allinonenepal.com').split(',')

# Expose X-Guest-Token so the browser can read it from responses (guest cart fallback)
CORS_EXPOSE_HEADERS = ['X-Guest-Token']

# Allow X-Guest-Token to be sent by the client in cross-origin requests
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-guest-token',  # Guest cart token fallback for cross-origin environments
]

# Cache - Redis for production
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'allinone-cache',
        }
    }

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Media Storage Strategy
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api

    cloudinary.config( 
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
        api_key = os.getenv('CLOUDINARY_API_KEY'), 
        api_secret = os.getenv('CLOUDINARY_API_SECRET'),
        secure = True
    )
except ImportError:
    pass

# Cloudinary Storage Configuration (for django-cloudinary-storage)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    'SECURE': True,
    'PREFIX': 'media'
}

STORAGES = {
    "default": {
        "BACKEND": os.getenv('MEDIA_STORAGE_BACKEND', 'cloudinary_storage.storage.MediaCloudinaryStorage'),
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Ensure compatibility for 3rd party apps
DEFAULT_FILE_STORAGE = STORAGES["default"]["BACKEND"]
STATICFILES_STORAGE = STORAGES["staticfiles"]["BACKEND"]

# WhiteNoise settings
WHITENOISE_MANIFEST_STRICT = False

# Logging - Console only for production (Render recommendation)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
