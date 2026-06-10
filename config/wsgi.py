"""
WSGI config for allinonenepal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Default to dev settings, use DJANGO_SETTINGS_MODULE environment variable to override
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

application = get_wsgi_application()
