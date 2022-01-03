import uuid

from django.db import models


class LotCode(models.Model):

    class Meta:
        unique_together = ('product', 'lot_number',)

    def __str__(self):
        return self.lot_number

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    product = models.ForeignKey('Product', on_delete=models.PROTECT,
                                related_name='lot_codes_set')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    lot_number = models.CharField(
        max_length=100, null=True, blank=True)
