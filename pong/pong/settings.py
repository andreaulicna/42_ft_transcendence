"""
Django settings for pong project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
from datetime import timedelta
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#kdp+9sp=#50r6qbmq$z-j8l9s3(5*i+78bk^7+z3s2!eeb!ja'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# # In settings.py
# DATABASE_READY = False

# # At startup
# while not DATABASE_READY:
#   try:
#     django.db.connections['default'].ensure_connection()
#   except Exception:
#     time.sleep(1)
#   else:
#     DATABASE_READY = True

# # Run migrations now
# if not DATABASE_READY:
#   print('Applying migrations...')
#   os.system('python manage.py migrate')


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
	'rest_framework_simplejwt.token_blacklist'
]

ASGI_APPLICATION = "pong.asgi.application"

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

ROOT_URLCONF = 'pong.urls'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
		'pong.authenticate.CustomJWTAuthentication'
		#'authentication.authenticate.CookieJWTAuthentication'
		#'rest_framework_simplejwt.authentication.JWTAuthentication',
        #'rest_framework.authentication.TokenAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
	'BLACKLIST_AFTER_ROTATION' : True,
	'AUTH_COOKIE': 'refresh_token',  # Cookie name. Enables cookies if value is set.
	'AUTH_COOKIE_DOMAIN': None,     # A string like "example.com", or None for standard domain cookie.
	'AUTH_COOKIE_SECURE': False,    # Whether the auth cookies should be secure (https:// only).
	'AUTH_COOKIE_HTTP_ONLY' : True, # Http only cookie flag.It's not fetch by javascript.
	'AUTH_COOKIE_PATH': reverse_lazy('login-refresh'),        # The path of the auth cookie.
	'AUTH_COOKIE_SAMESITE': 'Lax',  # Whether to set the flag restricting cookie leaks on cross-site requests.
									# This can be 'Lax', 'Strict', or None to disable
}

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

WSGI_APPLICATION = 'pong.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'HOST': 'localhost',
#         'PORT': 5432,
#         'NAME': 'mydb',
#         'USER': 'plouda',
#         'PASSWORD': os.getenv('DBPASS')
#     },
# }
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'postgres',
		'USER': 'postgres',
		'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'user_management_db',
		'PORT': '5432',
	#	'TEST': {
	#		'NAME': 'postgres-test'
	#	},
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

#TIME_ZONE = 'CET'
USE_TZ = True

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# def show_toolbar(request):
#     return True
# DEBUG_TOOLBAR_CONFIG = {
#     "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
# }

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
}

GAME_CONSTANTS['PADDLE_HEIGHT'] = GAME_CONSTANTS['GAME_HEIGHT'] / 5
GAME_CONSTANTS['PADDLE_WIDTH'] = 3


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}