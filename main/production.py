import os
from main.settings import *
from main.settings import BASE_DIR

from azure.identity import DefaultAzureCredential


ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
DEBUG = False
# SECRET_KEY = os.environ['SECRET_KEY']

INSTALLED_APPS += [
    "corsheaders",
    "storages",
]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    # 'django.middleware.cache.UpdateCacheMiddleware',  # new middleware cache
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',  # new middleware cache after
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
AZURE_ACCOUNT_NAME = os.environ['AZURE_ACCOUNT_NAME']
AZURE_CONTAINER = os.environ['AZURE_CONTAINER']
AZURE_ACCOUNT_KEY = os.environ['AZURE_ACCOUNT_KEY']
AZURE_STORAGE_URL = os.environ['AZURE_STORAGE_URL']

# Media files configuration
AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# STORAGES setting for Django 5.x

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "account_name": AZURE_ACCOUNT_NAME,
            "account_key": AZURE_ACCOUNT_KEY,
            "azure_container": AZURE_CONTAINER,
            "expiration_secs": None,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "ROSETTA_STORAGE_CLASS": {
        "BACKEND": "rosetta.storage.CacheRosettaStorage",
    },
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Compressor settings
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_ENABLED = True

# Cache configuration with Redis (commented out but ready for use)
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": os.environ.get('AZURE_REDIS_CONNECTIONSTRING'),
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
#         },
#     }
# }

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}
