from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from model_utils import Choices

from utils.models import CustomModel

User = get_user_model()

INTERNAL_STATUS_CHOICES = Choices(
    ('not_yet_picked', 'Not Yet Picked'),
    ('designing', 'Designing'),
    ('plate_making', 'Plate Making'),
    ('pending_printing', 'Pending Printing'),
    ('in_printing', 'In Printing'),
    ('in_binding', 'In Binding'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
    ('unmet_conditions', 'Order Issue'),
)

ERROR_STATUS_CHOICES = Choices(
    ('stuck_in_status', 'Stuck In Status'),
    ('missing_inventory', 'Missing Inventory'),
    ('hold_requested', 'Hold Requested'),
)


class Order(CustomModel):
    def __str__(self):
        return f"{self.tracking_id} - {self.name}"
    tracking_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True, default=None)
    customer = models.ForeignKey(
        'Customer', on_delete=models.PROTECT,
        default=None, null=True, blank=True,
        related_name='orders'
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
