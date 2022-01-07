from django.db import models
from localflavor.in_.models import INStateField


class Customer(models.Model):
    def __str__(self):
        return f"{self.name} | {self.city}"

    name = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(max_length=128, db_index=True, blank=True, null=True, default=None)
    phone = models.CharField(max_length=10, db_index=True, blank=True, null=True, default=None)

    address_1 = models.CharField(max_length=128)
    address_2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=64, )
    state = INStateField()
    zip_code = models.CharField(max_length=6, )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
