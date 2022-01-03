from django.db import models
from model_utils import Choices
from localflavor.in_.models import INStateField

LOCATION_TYPES = Choices(
    ('warehouse', 'Warehouse'),
    ('factory', 'Factory'),
)


class Warehouse(models.Model):
    name = models.CharField(
        blank=True, null=True, max_length=100
    )
    description = models.CharField(
        blank=True, null=True, max_length=400, help_text="Description of the warehouse."
    )

    business_name = models.CharField(max_length=250, default='Ohi Technologies')
    address_1 = models.CharField(max_length=128)
    address_2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=64, )
    state = INStateField()
    zip_code = models.CharField(max_length=6,)
    phone = models.CharField(max_length=10)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    short_code = models.CharField(
        max_length=25, blank=True, null=True,
        help_text="Shortcode for this address. (ie. MA1, BK1, LA1, etc)"
    )
    location_type = models.CharField(
        max_length=50, choices=LOCATION_TYPES,
        default=LOCATION_TYPES.factory
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
