from django.contrib.auth import get_user_model
from django.db import models
from model_utils import Choices

User = get_user_model()

REASON_CHOICES = Choices(
    ('order_reserved', 'Order Reserved'),
    ('order_fulfilled', 'Order Fulfilled'),
    ('order_canceled', 'Order Canceled'),
    ('inventory_received', 'Inventory Received'),
    ('inventory_reversal', 'Inventory Reversal'),
    ('inventory_slippage', 'Inventory Slippage'),
)


class InventoryAdjustment(models.Model):
    REASON_CHOICES = REASON_CHOICES

    def __str__(self):
        return "{} - {} - {}".format(
            self.inventory.warehouse.name,
            self.inventory.product.sku,
            self.inventory.product.title,
        )

    inventory = models.ForeignKey('Inventory', on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=None, null=True)
    order = models.ForeignKey(
        'Order', default=None, null=True,
        blank=True, on_delete=models.PROTECT
    )
    line_item = models.ForeignKey(
        'LineItem', default=None, null=True,
        blank=True, on_delete=models.PROTECT
    )
    unordered_change = models.IntegerField(default=0)
    ordered_change = models.IntegerField(default=0)
    fulfilled_change = models.IntegerField(default=0)
    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
        default=None
    )
    comment = models.CharField(
        max_length=255,
        null=True,
        default=None,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
