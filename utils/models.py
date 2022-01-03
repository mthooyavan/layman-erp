import random

from django.db import models
from django.utils import timezone


def slug_generator() -> str:
    """
    Generates and returns a unique string of length 10-11
    Examples: 8273176561, 10153962259
    """
    return str(int(timezone.now().timestamp()) + random.randint(1, 9999999999))


class AutoUpdateMixin:
    """
    By default Django doesn't update `auto_now` field if `update_fields` is used while saving an object.
    This mixin makes sure that `auto_now` is updated along with `update_fields`

    Note:
        - It expects an `auto_now` field in the model named `updated_at` i.e.
            updated_at = models.DateTimeField(auto_now=True)

        - It doesn't have any affect on the Model.objects.update method (which also doesn't update `auto_save` field)
    """

    def save(self, *args, **kwargs):

        if kwargs.get('update_fields'):
            kwargs['update_fields'] = list(set(list(kwargs['update_fields']) + ['updated_at']))

        super().save(*args, **kwargs)


class CustomModel(AutoUpdateMixin, models.Model):
    """
    This model should be inherited by all models of the codebase.
    """
    class Meta:
        abstract = True
