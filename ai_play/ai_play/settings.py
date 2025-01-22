"""
Django settings for ai_play project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta
from django.urls import reverse_lazy
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--5rzunb2-@)la00=4y(!5m#+@i_+gudqin+g^5l05%@n6u0rt7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	"debug_toolbar",
	"django_extensions",
	'rest_framework',
	'rest_framework.authtoken',
	'api',
	'corsheaders',
	'channels',
	'rest_framework_simplejwt.token_blacklist',
	'django.contrib.postgres'
]

ASGI_APPLICATION = 'ai_play.asgi.application'

AUTH_USER_MODEL = 'api.CustomUser'

MIDDLEWARE = [
	"debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
	'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
    }
}
# CORS_ALLOWED_ORIGINS = [
#     "http://127.0.0.1:5500",
#     "http://localhost:5500",
# ]
# Or allow all origins (not recommended for production)
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
		'ai_play.authenticate.CustomJWTAuthentication'
		#'authentication.authenticate.CookieJWTAuthentication'
		#'rest_framework_simplejwt.authentication.JWTAuthentication',
        #'rest_framework.authentication.TokenAuthentication',
    ],
}

ROOT_URLCONF = 'ai_play.urls'

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

WSGI_APPLICATION = 'matchmaking.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD':  os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'user_management_db',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

INTERNAL_IPS = [
    "127.0.0.1",
	"192.168.64.1"
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'CET'
USE_TZ = True

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_TRUSTED_ORIGINS = ["http://localhost:4200", "http://localhost", "http://localhost:5500"]

CHANNEL_LAYERS = {
	"default": {
		"BACKEND": "channels_redis.core.RedisChannelLayer",
		"CONFIG": {
			"hosts": [("redis", 6379)],
		},
	},
}

GAME_CONSTANTS = {
	'GAME_HEIGHT': 100,
	'GAME_WIDTH': 160,
	'BALL_SIZE': float(os.getenv('BALL_SIZE')),
	'BALL_SPEED': float(os.getenv('BALL_SPEED')),
	'PADDLE_SPEED': float(os.getenv('PADDLE_SPEED')),
	'MAX_SCORE': int(os.getenv('MAX_SCORE')),
}

GAME_CONSTANTS['PADDLE_HEIGHT'] = GAME_CONSTANTS['GAME_HEIGHT'] / 5
GAME_CONSTANTS['PADDLE_WIDTH'] = 4

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")