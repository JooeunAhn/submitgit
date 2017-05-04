from .common import *


DEBUG = False
# TODO SET URLS
ALLOWED_HOSTS = ['*']

# TODO DATABASE SETTINGS(AWS AURORA DB)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST':
        "submitgit-dev.ctxhubej0omd.ap-northeast-2.rds.amazonaws.com",
        "PORT": 3306,
        "USER": "root",
        "PASSWORD": load_credential('RDS_PASSWORD'),
        "NAME": "submitgit",
    }
}

# Health checker settings

INSTALLED_APPS += [
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.s3boto_storage',
]

if load_credential("SERVER_SOFTWARE").startswith('ElasticBeanstalk'):
    from django.core.exceptions import ImproperlyConfigured
    import requests
    try:
        def get_ec2_hostname():
            ipconfig = 'http://169.254.169.254/latest/meta-data/local-ipv4'
            return requests.get(ipconfig, timeout=10).text
        ALLOWED_HOSTS.append(get_ec2_hostname())
    except:
        raise ImproperlyConfigured(
            "You have to be running on AWS to use AWS settings")

# Sentry settings
INSTALLED_APPS += ['raven.contrib.django.raven_compat']

RAVEN_CONFIG = {
    'dsn': load_credential('SENTRY_DSN'),
}
