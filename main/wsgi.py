"""
WSGI config for main project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


settings_module = 'main.production' if 'WEBSITE_HOSTNAME' in os.environ else 'main.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)


application = get_wsgi_application()
