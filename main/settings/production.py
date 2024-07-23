import os
from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = [os.environ["WEBSITE_HOSTNAME"]]
# CORS HEADER
CORS_ALLOWED_ORIGINS = ["https://" + os.environ["WEBSITE_HOSTNAME"],]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
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
parameters = {pair.split("="):pair.split("=")[1] for pair in connection_string.split(" ")}
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
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
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