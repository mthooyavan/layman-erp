from django.conf import settings
from django.contrib.auth import get_user_model


# pylint: disable=invalid-name
User = get_user_model()


def system_user(username=None):
    # A system user to be used by celery tasks or any other change that isn't made by an actual user
    username = username or 'background_job_user'
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return User.objects.create_user(username=username, is_active=False)
