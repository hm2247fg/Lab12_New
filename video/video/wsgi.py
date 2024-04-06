"""
WSGI config for video project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Set the DJANGO_SETTINGS_MODULE environment variable to 'video.settings'
# This specifies the settings module for the Django application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video.settings')

# Retrieve the WSGI application object for the Django project
application = get_wsgi_application()
