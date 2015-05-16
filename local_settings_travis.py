DEBUG = False
SSL_ENABLED = False

SECRET_KEY = 'travis-ci'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fc_test_db',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'STORAGE_ENGINE': 'MyISAM',
    }
}

PAYPAL_ACCOUNT_EMAIL = 'not@valid.net'
SERVER_EMAIL = "not@valid.net"

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''

SOCIAL_AUTH_RUNKEEPER_KEY = ''
SOCIAL_AUTH_RUNKEEPER_SECRET = ''

SOCIAL_AUTH_MAPMYFITNESS_KEY = ''
SOCIAL_AUTH_MAPMYFITNESS_SECRET = ''

PIPELINE_ENABLED = False
STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

DISQUS_SHORTNAME = "invalid"

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost']
BASE_URL = 'http://localhost'

#celery broker (RabbitMQ)
BROKER_URL = "amqp://guest:guest@localhost//"

GOOGLE_ANALYTICS_TRACKING_ID = ''

WITHINGS_USER_NAME = ''
WITHINGS_PASSWORD = ''

LOCALE = 'en_US.utf8'