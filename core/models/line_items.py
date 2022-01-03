import uuid

from django.db import models


class LineItem(models.Model):
    def __str__(self):
        return '{} - {}'.format(self.product, self.order)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(
        'Order', default=None, null=True, blank=True,
        on_delete=models.PROTECT, related_name='line_item_set'
    )
    receipt = models.ForeignKey(
        'Receipt', default=None, null=True, blank=True,
        on_delete=models.PROTECT, related_name='line_item_set'
    )
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def order_tracking_id(self) -> str:
        return self.order.tracking_id
