"""
WSGI config for main project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from main.settings import base

from django.core.wsgi import get_wsgi_application

if base.DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.production')



application = get_wsgi_application()
