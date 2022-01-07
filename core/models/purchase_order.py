from django.contrib.auth import get_user_model
from django.db import models

from utils.models import CustomModel

User = get_user_model()


class PurchaseOrder(CustomModel):
    def __str__(self):
        return f"{self.tracking_id} - {self.vendor}"
    tracking_id = models.CharField(max_length=100, unique=True, db_index=True)
    vendor = models.ForeignKey(
        'Vendor', on_delete=models.PROTECT,
        default=None, null=True, blank=True,
        related_name='purchase'
    )

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        null=True, default=None, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def tracking_sha(self):
        return self.tracking_id[:6]
