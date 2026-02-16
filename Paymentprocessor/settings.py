from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o2uhc0-%t1n48)7%@b=g6rww*ko3wd&_u4=tliv3$@zfs+2hm@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Paymentprocessor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'Paymentprocessor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS =[
    (BASE_DIR/ 'static')
]
STATIC_ROOT = (BASE_DIR / 'assets')
MEDIA_URL = '/media/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "payments.api.authentication.APIKeyAuthentication",
    ],
}




DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# AUTH_USER_MODEL = "payments.User"




MPESA_CONSUMER_KEY = config("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = config("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = config("MPESA_SHORTCODE")
MPESA_PASSKEY = config("MPESA_PASSKEY")
MPESA_CALLBACK_URL = config("MPESA_CALLBACK_URL")
MPESA_ENVIRONMENT = config("MPESA_ENVIRONMENT")






##############################################
## logs management start ########################
LOG_DIR = os.path.join(BASE_DIR, "logs")

# create logs directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "{asctime} | {levelname} | {name} | {message}",
            "style": "{",
        },
    },

    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "payments.log"),
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "errors.log"),
            "formatter": "verbose",
        },


    },

    "loggers": {
        "payments": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
## logs management end ########################
##############################################
