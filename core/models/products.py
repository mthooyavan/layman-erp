from django.db import models
from model_utils import Choices

PRODUCT_TYPE = Choices(
    ('paper', 'Paper'),
    ('ink', 'Ink'),
    ('plate', 'Plate'),
)


class Product(models.Model):
    class Meta:
        unique_together = ('sku', 'title', 'type', 'variant')

    sku = models.CharField(db_index=True, max_length=50)
    title = models.CharField(db_index=True, max_length=255)
    type = models.CharField(
        db_index=True, max_length=10,
        choices=PRODUCT_TYPE, default=PRODUCT_TYPE.paper
    )
    variant = models.CharField(db_index=True, max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disabled_at = models.DateTimeField(db_index=True, null=True, default=None, blank=True)
