import os
from . settingslocal import *

#APP_NAME=settingslocal.APP_NAME
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = settingslocal.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = settingslocal.DEBUG

#ALLOWED_HOSTS = settingslocal.ALLOWED_HOSTS

# Application definition
INSTALLED_APPS = [
    # customizzazione gestione degli utenti
    'accounts',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_admin_multiple_choice_list_filter',

    'unical_template',
    'sass_processor',
    'bootstrap_italia_template',
    'unical_agid_template',

    'rangefilter',
    'ldapdb',
    'ldap_peoples',
    'identity',
    'provisioning',

    'cineca_repl',
]

if 'provisioning' in INSTALLED_APPS:
    from provisioning.settings import *

if 'ldap_peoples' in INSTALLED_APPS:
    from ldap_peoples.settings import *
    # otherwise overload whatever needed...
    # import ldap_peoples.settings as ldap_peoples_settings
    # LDAP_DATETIME_FORMAT = ldap_peoples_settings.LDAP_DATETIME_FORMAT
    # LDAP_DATETIME_MILLISECONDS_FORMAT = ldap_peoples_settings.LDAP_DATETIME_MILLISECONDS_FORMAT
    # PPOLICY_PERMANENT_LOCKED_TIME = ldap_peoples_settings.PPOLICY_PERMANENT_LOCKED_TIME
    # PPOLICY_PASSWD_MAX_LEN= ldap_peoples_settings.PPOLICY_PASSWD_MAX_LEN
    # PPOLICY_PASSWD_MIN_LEN= ldap_peoples_settings.PPOLICY_PASSWD_MIN_LEN

    # PASSWD_FIELDS_MAP = ldap_peoples_settings.PASSWD_FIELDS_MAP
    # SECRET_PASSWD_TYPE = ldap_peoples_settings.SECRET_PASSWD_TYPE
    # DISABLED_SECRET_TYPES = ldap_peoples_settings.DISABLED_SECRET_TYPES
    # DEFAULT_SECRET_TYPE = ldap_peoples_settings.DEFAULT_SECRET_TYPE
    # SECRET_FIELD_VALIDATORS = ldap_peoples_settings.SECRET_FIELD_VALIDATORS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Messages were getting stored in CookiesStorage, but for some weird reason the Messages in CookiesStorage were getting expired or deleted for the 2nd request
# MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# GETTEXT LOCALIZATION
MIDDLEWARE.append('django.middleware.locale.LocaleMiddleware')
LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)
#

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

AUTHENTICATION_BACKENDS = [
                            'ldap_peoples.auth.LdapAcademiaAuthBackend',
                            'django.contrib.auth.backends.ModelBackend',
                            # FIX TODO in Django 2.1
                            # 'django_idm.auth.SessionUniqueBackend',
                          ]
AUTH_USER_MODEL = 'accounts.User'
ROOT_URLCONF = 'django_idm.urls'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/dashboard'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'django_idm.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# LDAP_BASEDN = settingslocal.LDAP_BASEDN
# DATABASES = settingslocal.DATABASES
# DATABASE_ROUTERS = settingslocal.DATABASE_ROUTERS

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# LANGUAGE_CODE = settingslocal.LANGUAGE_CODE
# TIME_ZONE = settingslocal.TIME_ZONE
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATA_UPLOAD_MAX_NUMBER_FIELDS = 34096

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "{} %H:%M:%S".format(DATE_FORMAT)

DATE_INPUT_FORMATS = [DATE_FORMAT, "%Y-%m-%d"]
DATETIME_INPUT_FORMATS = ["{} %H:%M:%S".format(i) for i in DATE_INPUT_FORMATS]
# print('DATETIME_INPUT_FORMATS', DATETIME_INPUT_FORMATS)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(DATA_DIR, 'static')

# By default, staticfiles will look for files within the static/ directory
# of each installed app, as well as in directories defined in STATICFILES_DIRS.
# This behaviour depends on backends listed in STATICFILES_FINDERS.
#STATICFILES_FINDERS = [
    #'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#]

#STATICFILES_DIRS = [
    #os.path.join(STATIC_ROOT, ''),
#]

MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
MEDIA_URL = '/media/'
