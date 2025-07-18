"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import base64
import os
from pathlib import Path
from datetime import timedelta

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [ "*" ]
CORS_ALLOW_ALL_ORIGINS = True
if 'CODESPACE_NAME' in os.environ:
    CSRF_TRUSTED_ORIGINS = [f'https://{os.getenv("CODESPACE_NAME")}-8000.{os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")}']


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load private key
PRIVATE_KEY = base64.b64decode(os.getenv("PRIVATE_KEY_B64", ""))
# with open(os.path.join(BASE_DIR, 'cert/private_key.pem'), 'rb') as f:
#     PRIVATE_KEY = f.read()
# Load public key
PUBLIC_KEY = base64.b64decode(os.getenv("PUBLIC_KEY_B64", ""))
# with open(os.path.join(BASE_DIR, 'cert/public_key.pem'), 'rb') as f:
#     PUBLIC_KEY = f.read()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
# python -c 'import secrets; print(secrets.token_hex())'
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third-party
    "corsheaders",
    'rest_framework',
    'django_filters',
    'oauth2_provider',
    'rest_framework.authtoken',
    'compressor',
    'rosetta',  # http://127.0.0.1:8000/rosetta/pick/?rosetta
    'drf_yasg',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # AllAuth
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.telegram',
    # My apps
    'user',
    'administrator',
    'ads',
    'schools',
    'health_check',
    'api',
    'organization',
    'search',
    'web'
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'oauth2_provider.backends.OAuth2Backend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',  # OAuth2
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'user.middleware.profile.EnsureProfileMiddleware',
    "allauth.account.middleware.AccountMiddleware", # allauth
    'api.middlewares.LogRequestMiddleware',
]

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# Ensure SESSION settings are properly configured
SESSION_COOKIE_NAME = "auth_server_sessionid"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
# Application definition
ROOT_URLCONF = 'main.urls'

# JWT settings
JWT_AUTH = {
    'JWT_PRIVATE_KEY': PRIVATE_KEY,
    'JWT_PUBLIC_KEY': PUBLIC_KEY,
    'JWT_ALGORITHM': 'RS256',
    'JWT_EXPIRATION_DELTA': timedelta(seconds=3600),
}
# OAuth2 Settingss
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Authentication Server OAuth2 Settings
AUTH_USER_MODEL = 'user.User'
# User Login 2Auth
# LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL='profiles:profile'
LOGIN_URL = '/accounts/login/'


WSGI_APPLICATION = 'main.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('km', 'Khmer'),
    # ...
]
TIME_ZONE = 'Asia/Phnom_Penh'
USE_I18N = True
USE_I18N_STANDARD = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# Base settings
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# # Storage configuration using STORAGES setting
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        'OPTIONS': {
            'location': MEDIA_ROOT,
        },
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        'OPTIONS': {
            'location': STATIC_ROOT,
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',      
    ),
}

# Provider specific settings
TELEGRAM_BOT_ID = os.getenv('TELEGRAM_BOT_ID')
TELEGRAM_LOGIN_PUBLIC_KEY = os.getenv('TELEGRAM_LOGIN_PUBLIC_KEY')
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'openid',
            'https://www.googleapis.com/auth/calendar.readonly'
        ],
        'APP': {
            'client_id': os.getenv("GOOGLE_AUTH_CLIENT_ID"),
            'secret': os.getenv("GOOGLE_AUTH_SECRET"),
            # 'key': ''
        },
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'consent'
        }
    },
    'facebook': {
        'METHOD': 'oauth2',  # Set to 'js_sdk' to use the Facebook connect SDK
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
        'GRAPH_API_URL': 'https://graph.facebook.com/v13.0',
    },
    'telegram': {
        'APP': {
            'client_id': TELEGRAM_BOT_ID,

            # NOTE: For the secret, be sure to provide the complete bot token,
            # which typically includes the bot ID as a prefix.
            'secret': TELEGRAM_LOGIN_PUBLIC_KEY,
        },
        'AUTH_PARAMS': {'auth_date_validity': 100},
    }
}

# Cirtificate Settings
# Path to your private and public keys for JWT
JWT_PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_B64", "")
JWT_PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_B64", "")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APP_URL = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else [os.getenv("APP_URL")]
OPEN_AI_API_SECRET=os.getenv("OPEN_AI_KEY")
SOCIALACCOUNT_LOGIN_ON_GET = True
