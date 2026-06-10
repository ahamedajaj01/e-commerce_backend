"""
Development Django settings for allinonenepal project.
Extends base.py with development-specific settings.
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dev-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database - using SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db_v2.sqlite3'),
    }
}

# Email Backend - Console output for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS for frontend development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
]

# Django Extensions (optional but useful)
INSTALLED_APPS += [
    'django_extensions',
]

# Cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'allinonenepal-cache',
    }
}

# REST Framework - More detailed errors in development
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# Print SQL queries in console
if DEBUG:
    import logging
    logging.getLogger('django.db.backends').setLevel(logging.DEBUG)
