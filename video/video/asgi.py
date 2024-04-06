"""
ASGI config for video project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Set the DJANGO_SETTINGS_MODULE environment variable to 'video.settings'
# This specifies the settings module for the Django application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video.settings')

# Retrieve the ASGI application object for the Django project
application = get_asgi_application()
