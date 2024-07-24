import os
from .base import *
from urllib.parse import urlparse


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = [os.environ["WEBSITE_HOSTNAME"], "169.254.130.6", "169.254.130.6:8000", "*"]
# CORS HEADER
# CORS_ALLOWED_ORIGINS = ["https://" + os.environ["WEBSITE_HOSTNAME"]]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.cache.UpdateCacheMiddleware',  # new middleware cache
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # new middleware cache after
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
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
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
    raise ValueError(
        "Database connection string is not set in environment variables.")
    
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# CACHE WITH REDIS
# Fetch the Redis connection string from environment variables
redis_connection_string = os.environ.get("AZURE_REDIS_CONNECTIONSTRING")
if not redis_connection_string:
    raise ValueError("Redis connection string is not set in environment variables.")

# Parse the connection string
parsed_url = urlparse(redis_connection_string)

# Extract the password, hostname, and port
redis_password = parsed_url.password
redis_host = parsed_url.hostname
redis_port = parsed_url.port

# Configure the Django CACHES setting
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"rediss://{redis_host}:{redis_port}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": redis_password,
            "SSL_CERT_REQS": None,  # Use this if SSL certificate verification is not required
        }
    }
}
# Optional: Cache settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Static files (CSS, JavaScript, Images)
# STATIC_HOST = os.environ.get("DJANGO_STATIC_HOST", "")
# STATIC_URL = STATIC_HOST + "/static/"
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Compressor Settings
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_ENABLED = True

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

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
