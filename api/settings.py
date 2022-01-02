import os
from datetime import timedelta

import environ

# django-environ is being used to enable environment variable parsing/casting
ENV = environ.Env()
# Load all the environment variables
environ.Env.read_env()


def env_get(key, default=None):
    return os.environ.get(key, default)


ENVIRONMENT = ENV('ENVIRONMENT', default='development')
ENVIRONMENT_COLOR = '#FF0000' if ENVIRONMENT == 'production' else '#F4C430' if ENVIRONMENT == 'staging' else '#808080'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PAGINATION_CLASS': 'api.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        'standard': '500/minute'
    },

    'EXCEPTION_HANDLER': 'api.exceptions.exception_handler'

}

if ENVIRONMENT == 'production':
    # This disables the 'browsable' api that can cuase various production issues
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=50)
}

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'api.swagger.CustomAutoSchema',
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': True
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 30  # After 30 minutes
SESSION_SAVE_EVERY_REQUEST = True
