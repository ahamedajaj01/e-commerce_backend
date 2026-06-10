"""
ASGI config for allinonenepal project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Default to dev settings, use DJANGO_SETTINGS_MODULE environment variable to override
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

application = get_asgi_application()
