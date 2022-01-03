import uuid

from django.contrib.auth import get_user_model
from django.db import models

from utils.models import CustomModel

User = get_user_model()


class Receipt(CustomModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receiving_centre = models.ForeignKey('Warehouse', on_delete=models.PROTECT, related_name='inventory_shipments')
    po_number = models.CharField(max_length=128, help_text='PO number for this shipment', blank=True, null=True)

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        null=True, default=None, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.po_number} @ {self.receiving_centre}'
