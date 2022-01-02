"""
context processors for shopify_fulfillment
"""
from django.conf import settings


def api_keys(request):  # pylint: disable=unused-argument
    """
    Pass a `APIKEYS` dictionary into the template context, which holds
    IDs and secret keys for the various APIs used in this project.
    """
    return {
        "APIKEYS": {
        }
    }


def environment_variables(request):  # pylint: disable=unused-argument
    """
    Pass a `APIKEYS` dictionary into the template context, which holds
    IDs and secret keys for the various APIs used in this project.
    """
    return {
        'ENVIRONMENT_NAME': settings.ENVIRONMENT,
        'ENVIRONMENT_COLOR': settings.ENVIRONMENT_COLOR,
    }
