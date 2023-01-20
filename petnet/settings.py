"""
Django settings for petnet project.

Generated by 'django-admin startproject' using Django 3.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^9w$a(ac2r18*wo2lzym&l&6=i7-t2kggc#x0slj6xex)4kus*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

SESSION_COOKIE_AGE = 86400
CART_SESSION_ID = 'cart'

LOGIN_URL= 'login'
LOGOUT_REDIRECT_URL = 'frontpage'
LOGIN_REDIRECT_URL ='/'

# Application definition

INSTALLED_APPS = [
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    #3rd party packages
    'widget_tweaks',
    'crispy_forms',
    
    #apps    
    'core',
    'userprofile',
    'Shipping',
    'store',
    
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

ROOT_URLCONF = 'petnet.urls'


WEB_SITE_URL = 'http://127.0.0.1:8000/' if DEBUG else 'http:zeus28.pythonanywhere.com/'
STRIPE_PUB_KEY = 'pk_test_51J3Bu4Ls0fNtt2ThkrZFwNQm4IUae2tDoWj6SF6nTnNRq3RKTeqFCi2OGABF4nWSsii9SuNpFUsPZTTecHkGLyyT00juewjaNm'
STRIPE_SECRET_KEY = 'sk_test_51J3Bu4Ls0fNtt2Thxkx9pVLi5gmvdnRxkfdT39kTj1n1QhkhFJh1OQuioiIxvwhCWm3twdMT6gKUZAUPkDktE2PM00ZgMDk2jF'


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
                
                #custom context processor
                'store.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'petnet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES={
        'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zeus28$default',
        'USER': 'zeus28',
        'PASSWORD': 'Bardo28@',
        'HOST': 'zeus28.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
if not DEBUG:
    #STATIC_ROOT = os.path.join(BASE_DIR, "static")
    STATICFILES_DIRS = [
            BASE_DIR / 'static'
        ]
    
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    STATIC_URL = '/static/'
if DEBUG:
    
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    STATIC_URL = '/static/'
    #STATIC_ROOT = BASE_DIR / 'static'
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
