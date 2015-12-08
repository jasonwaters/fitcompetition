# Django settings for fitcompetition project.
from __future__ import absolute_import
import cssutils
import logging
import manage
import os

DEBUG = False

ADMINS = (
    ('Jason Waters', 'jason@myheck.net'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Denver'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

PROJ_ROOT = os.path.dirname(os.path.realpath(manage.__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJ_ROOT, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'pipeline.finders.PipelineFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'fitcompetition.middleware.SocialAuthExceptionMiddleware',
    'dealer.contrib.django.Middleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'fitcompetition.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'fitcompetition.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'grappelli',
    'django.contrib.admin',
    'rest_framework',
    'social.apps.django_app.default',
    'pipeline',
    'storages',
    'djcelery',
    'seacucumber',
    'debug_toolbar',
    'django_premailer',
    'fitcompetition',
)

cssutils.log.setLevel(logging.CRITICAL)

API_PAGE_SIZE = 50

REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend', 'rest_framework.filters.OrderingFilter'),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',),

    'PAGINATE_BY': API_PAGE_SIZE
}

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'

PIPELINE_CSS = {
    'all-css': {
        'source_filenames': (
            'css/bootstrap.css',
            'css/font-awesome.css',
            'css/style.css',
        ),
        'output_filename': 'css/all.css',
    },
}

PIPELINE_JS = {
    'all-js': {
        'source_filenames': (
            'js/angular-resource.js',
            'js/angular-cookies.js',
            'js/angular-payments.js',
            'js/angular-slugify.js',
            'js/angular-ui-bootstrap-tpls.js',
            'js/ng/*.js',
            'js/ng/**/*.js',
            'js/jquery.cookie.js',
            'js/jquery.validate.js',
            'js/additional-methods.js',
            'js/bootstrap.js',
            'js/jstz.js',
            'js/moment.js',
            'js/lodash.js',
            "js/binaryajax.js",
            "js/exif.js",
            "js/canvasResize.js",
            'js/countdown.js',
            'js/script.js',
        ),
        'output_filename': 'js/all.js',
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJ_ROOT, 'logs/error.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTH_USER_MODEL = 'fitcompetition.FitUser'
SOCIAL_AUTH_USER_MODEL = 'fitcompetition.FitUser'
SOCIAL_AUTH_UID_LENGTH = 255
SOCIAL_AUTH_NONCE_SERVER_URL_LENGTH = 255
SOCIAL_AUTH_ASSOCIATION_SERVER_URL_LENGTH = 255
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 255


AUTHENTICATION_BACKENDS = (
    'fitcompetition.backends.runkeeper.RunkeeperOauth2',
    'fitcompetition.backends.mapmyfitness.MapMyFitnessOAuth',
    'fitcompetition.backends.strava.StravaOAuth',
    'django.contrib.auth.backends.ModelBackend'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    "django.core.context_processors.request",
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'dealer.contrib.django.context_processor',
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'fitcompetition.pipeline.post_login_tasks',
)

SOCIAL_AUTH_USER_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "fullname",
    "email"
]

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_DISABLE_RATE_LIMITS = False
CUCUMBER_RATE_LIMIT = 5

TEAM_MEMBER_MAXIMUM = 5

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/'

PYTHON_FOLDER_NAME = 'python2.7'

try:
    from local_settings import *
except:
    pass

SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
RAISE_EXCEPTIONS = DEBUG

AWS_HEADERS = {
    'Expires': 'access plus 1 year',
    'Cache-Control': 'max-age=86400',
}

DEFAULT_FILE_STORAGE = 'fitcompetition.s3utils.MediaS3BotoStorage'
S3_URL = 'http://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
MEDIA_DIRECTORY = '/media/'
MEDIA_URL = S3_URL + MEDIA_DIRECTORY

TEMPLATE_DEBUG = DEBUG
#a virutalenv should be created and located in a folder named "env" at the project root.
os.environ['PATH'] += ':' + os.path.join(PROJ_ROOT, 'env/bin')
SITE_PACKAGES_DIR = os.path.join(PROJ_ROOT, 'env', 'lib', PYTHON_FOLDER_NAME, 'site-packages')