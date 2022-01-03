import uuid

from django.db import models
from django.db.models import UniqueConstraint, Q


class Inventory(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['product', 'warehouse', 'lot_code'],
                             name='unique_with_lot_code'),
            UniqueConstraint(fields=['product', 'warehouse'],
                             condition=Q(lot_code=None),
                             name='unique_without_lot_code'),
        ]
        verbose_name_plural = "inventories"

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT)
    lot_code = models.ForeignKey('LotCode', on_delete=models.PROTECT, null=True, blank=True)
    location = models.ForeignKey('Location', on_delete=models.PROTECT, null=True, blank=True, default=None)

    unordered = models.IntegerField(db_index=True, default=0)
    ordered = models.IntegerField(default=0)
    fulfilled = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
