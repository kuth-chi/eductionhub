import os
import re

from main.settings import *
from main.settings import BASE_DIR

ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']
                 ] if 'WEBSITE_HOSTNAME' in os.environ else []
CUSTOM_DOMAIN = os.getenv('CUSTOM_DOMAIN')
WEBSITE_HOSTNAME = os.environ.get('WEBSITE_HOSTNAME')
ALLOWED_HOSTS += ["https://eduhubstorage.blob.core.windows.net",
                  "https://educationhub.io"]

# CSRF Trusted Origins - Critical for cross-subdomain authentication in production
CSRF_TRUSTED_ORIGINS = [
    "https://educationhub.io",
    "https://authz.educationhub.io",
]

# Add environment-specific domains
if 'WEBSITE_HOSTNAME' in os.environ:
    CSRF_TRUSTED_ORIGINS.append('https://' + os.environ['WEBSITE_HOSTNAME'])

CORS_ALLOWED_ORIGINS = [
    'https://eduhubstorage.blob.core.windows.net',
    "https://educationhub.io",
    "https://authz.educationhub.io",
]

# Add environment-specific CORS origins
if 'WEBSITE_HOSTNAME' in os.environ:
    CORS_ALLOWED_ORIGINS.append(f"https://{os.environ['WEBSITE_HOSTNAME']}")
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.blob\.core\.windows\.net$",
    r"^https://(\w+\.)*educationhub\.io$",
    r"^http://(\w+\.)*educationhub\.io$",
]

if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)
    CSRF_TRUSTED_ORIGINS.append('https://' + CUSTOM_DOMAIN)
    CORS_ALLOWED_ORIGINS.append('https://' + CUSTOM_DOMAIN)

if WEBSITE_HOSTNAME:
    CORS_ALLOWED_ORIGINS.append(f"https://{WEBSITE_HOSTNAME}")

# Cross-subdomain cookie domain for issuing frontend-readable JWT cookies from authz.*
# This allows the frontend on educationhub.io to include tokens when proxying to authz.educationhub.io
CROSS_SUBDOMAIN_COOKIE_DOMAIN = os.getenv(
    "CROSS_SUBDOMAIN_COOKIE_DOMAIN", ".educationhub.io")

# Additional allowed redirect hosts for cross-subdomain authentication
ALLOWED_REDIRECT_HOSTS = [
    "educationhub.io",
    "authz.educationhub.io",
]

# Add environment-specific redirect hosts
if CUSTOM_DOMAIN:
    ALLOWED_REDIRECT_HOSTS.append(CUSTOM_DOMAIN.replace(
        "https://", "").replace("http://", ""))
if WEBSITE_HOSTNAME:
    ALLOWED_REDIRECT_HOSTS.append(WEBSITE_HOSTNAME.replace(
        "https://", "").replace("http://", ""))

# Security settings for production
CORS_ALLOW_ALL_ORIGINS = False
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Session and JWT cookie settings for cross-subdomain authentication
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Required for cross-subdomain
SESSION_COOKIE_AGE = 1800

# JWT cookie settings for production (override development settings)
# These settings ensure JWT cookies work across subdomains
REST_AUTH = {
    'USE_JWT': True,
    'SESSION_LOGIN': True,
    'JWT_AUTH_COOKIE': 'access_token',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh_token',
    'JWT_AUTH_HTTPONLY': True,
    'JWT_AUTH_SECURE': True,  # Secure in production
    'JWT_AUTH_SAMESITE': 'Lax',  # Critical for cross-subdomain
    'USER_DETAILS_SERIALIZER': 'api.serializers.user_details.UserDetailsSerializer',
    'REGISTER_SERIALIZER': 'api.serializers.registration.CustomRegisterSerializer',
}

# Enhanced logging for production debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'app.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 730,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'rest_framework': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'dj_rest_auth': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

DEBUG = False
# SECRET_KEY = os.environ['SECRET_KEY']

INSTALLED_APPS += [
    "storages",
]

MIDDLEWARE += [

    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.gzip.GZipMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',  # new middleware cache
    # 'django.middleware.cache.FetchFromCacheMiddleware',  # new middleware cache after
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
if not DEBUG:
    connection_string = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    if connection_string:
        parameters = {pair.split("=")[0]: pair.split("=")[1]
                      for pair in connection_string.split(" ")}

        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": parameters["dbname"],
                "USER": parameters["user"],
                "PASSWORD": parameters["password"],
                "HOST": parameters["host"],
                "PORT": parameters["port"],
            }
        }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files (CSS, JavaScript, Images)
# Azure Storage settings
AZURE_ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME")
AZURE_CONTAINER = os.getenv("AZURE_CONTAINER")
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
AZURE_STORAGE_URL = os.getenv("AZURE_STORAGE_URL")

# Media files configuration
AZURE_CUSTOM_DOMAIN = f"{AZURE_ACCOUNT_NAME}.blob.core.windows.net"
MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
CSRF_TRUSTED_ORIGINS += [f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net"]

# STORAGES setting for Django 5.x
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "account_name": AZURE_ACCOUNT_NAME,
            "account_key": AZURE_ACCOUNT_KEY,
            "azure_container": AZURE_CONTAINER,
            "expiration_secs": 10,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "rosetta_storage_class": {
        "BACKEND": "rosetta.storage.CacheRosettaStorage",
    },
}


# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
        'TIMEOUT': 36000,
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'app.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 730,
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG' if DEBUG else 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}
