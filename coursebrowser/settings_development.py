import os, sys
from .secret import SECRET_KEY_IMPORT, DATABASE_PASSWORD_IMPORT

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_IMPORT

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ("*",)
EMAIL_ADDRESS = "info@kolibrisolutions.nl"
ADMINS = [("devteam", EMAIL_ADDRESS)]

NAME_CODE = "coursebrowser"
NAME_PRETTY = "Course Browser"
DOMAIN = "https://coursebrowser.nl"


# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'index',
    'studyguide',
    'templates',
    'osiris',

    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
]

ROOT_URLCONF = 'coursebrowser.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'coursebrowser.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}



# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
#
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = False

USE_L10N = False

USE_TZ = True

# overrides (only used if USE_L10N is False)
DATE_FORMAT = 'N j, Y'
SHORT_DATE_FORMAT = 'd-m-Y'
DATETIME_FORMAT = 'N j, Y, H:i'
SHORT_DATETIME_FORMAT = 'd-m-Y H:i'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/home/django/coursebrowser/templates/static/'

# Host for sending e-mail.
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
SERVER_EMAIL = "no-reply@kolibrisolutions.nl"
FROM_EMAIL_ADDRESS = SERVER_EMAIL

SESSION_COOKIE_AGE = 86400
LOGIN_REDIRECT_URL = '/'

# Use REDIS to cache certain pages and variables.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": 4*7*24*60*60, # one month
        "KEY_PREFIX": NAME_CODE,
    }
}

# Celery settings
BROKER_URL = 'redis://localhost:6379/2'  # our redis address
# use json format for everything
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

# channels, a new and better way to run Django including websockets.
ASGI_APPLICATION = 'coursebrowser.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
LOGGING = {
    'version': 1,
    'handlers': {
       'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
# Celery settings
BROKER_URL = 'redis://localhost:6379/2'  # our redis address
# use json format for everything
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

HTML_MINIFY = False
