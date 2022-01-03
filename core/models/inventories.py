from django.db import models
from model_utils import Choices

PRODUCT_TYPE = Choices(
    ('paper', 'Paper'),
    ('ink', 'Ink'),
    ('plate', 'Plate'),
)


class Inventory(models.Model):
    class Meta:
        verbose_name_plural = "inventories"

    def __str__(self):
        return '{} - {} {} - {}'.format(self.sku, self.name, self.variant, self.product_type)

    sku = models.CharField(db_index=True, unique=True, max_length=50)
    name = models.CharField(db_index=True, max_length=255)
    product_type = models.CharField(
        db_index=True, max_length=10,
        choices=PRODUCT_TYPE, default=PRODUCT_TYPE.paper
    )
    variant = models.CharField(db_index=True, max_length=255)

    unordered = models.IntegerField(db_index=True, default=0)
    ordered = models.IntegerField(default=0)
    fulfilled = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
