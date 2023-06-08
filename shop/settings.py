import os
from django.contrib.messages import constants as messages

import config

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

DEBUG = True

ALLOWED_HOSTS = ['*']

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static')
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STORAGE = os.path.join(BASE_DIR, 'storage')

SECRET_KEY = 'my_super_secret_key_1234567890987654321_!@#$%^&*()(*&^%$#@!'

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'django_rest_passwordreset',
    'djoser',
    'django_filters',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap4',
    'captcha',

    'backend',
    'authorization',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shop.urls'

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

WSGI_APPLICATION = 'shop.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config.DB_NAME,
        'USER': config.DB_USER,
        'PASSWORD': config.DB_PASSWORD,
        'HOST': config.DB_HOST,
        'PORT': config.DB_PORT,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

RECAPTCHA_PUBLIC_KEY = config.RECAPTCHA_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY = config.RECAPTCHA_PRIVATE_KEY
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
SERVER_EMAIL = EMAIL_HOST_USER

PASSWORD_RESET_TIMEOUT = 14400

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

AUTH_USER_MODEL = 'authorization.User'

AUTH_CONTACT_MODEL = 'authorization.Contact'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination'
                                '.PageNumberPagination',
    'PAGE_SIZE': 20,

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.TemplateHTMLRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',

    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle'
    ],
    'DEFAULT_PERMISSIONS_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/second',
        'user': '30/second'
    }
}

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000']

SPECTACULAR_SETTINGS = {
    'TITLE': 'shop',
    'DESCRIPTION': 'API Service for ordering goods for retail chains',
    'VERSION': '1.0.0',
}
