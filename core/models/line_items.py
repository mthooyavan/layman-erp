import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import InventoryAdjustmentLog
from core.models.inventory_adjustments import REASON_CHOICES, InventoryAdjustment
from utils.users import system_user


class LineItem(models.Model):
    def __str__(self):
        return '{} - {}'.format(self.inventory, self.order)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(
        'Order', on_delete=models.PROTECT, related_name='line_item_set',
        null=True, blank=True, default=None
    )
    purchase = models.ForeignKey(
        'PurchaseOrder', on_delete=models.PROTECT, related_name='line_item_set',
        null=True, blank=True, default=None
    )
    inventory = models.ForeignKey('Inventory', on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def order_tracking_id(self) -> str:
        return self.order.tracking_id if self.order else self.purchase.tracking_id if self.purchase else None


@receiver(post_save, sender=LineItem)
def post_save_hook(sender, instance, created, **kwargs):
    if created:
        if instance.order:
            inventory = instance.inventory
            inv_adj = InventoryAdjustment.objects.create(
                inventory=inventory,
                order=instance.order,
                line_item=instance,
                user=system_user(),
                unordered_change=-instance.quantity,
                ordered_change=instance.quantity,
                reason=REASON_CHOICES.order_reserved
            )
            inv_adj_log = InventoryAdjustmentLog.objects.create(
                inventory=inventory,
                source_adjustment=inv_adj,
                unordered_change=-instance.quantity,
                ordered_change=instance.quantity,
                absolute_pre_unordered=inventory.unordered,
                absolute_pre_ordered=inventory.ordered,
                absolute_post_unordered=inventory.unordered + inv_adj.unordered_change,
                absolute_post_ordered=inventory.ordered + inv_adj.ordered_change,
            )
            inventory.unordered = inv_adj_log.absolute_post_unordered
            inventory.ordered = inv_adj_log.absolute_post_ordered
            inventory.save()

        if instance.purchase:
            inventory = instance.inventory
            inv_adj = InventoryAdjustment.objects.create(
                inventory=inventory,
                purchase=instance.purchase,
                line_item=instance,
                user=system_user(),
                unordered_change=instance.quantity,
                ordered_change=0,
                reason=REASON_CHOICES.order_reserved
            )
            inv_adj_log = InventoryAdjustmentLog.objects.create(
                inventory=inventory,
                source_adjustment=inv_adj,
                unordered_change=instance.quantity,
                ordered_change=0,
                absolute_pre_unordered=inventory.unordered,
                absolute_pre_ordered=inventory.ordered,
                absolute_post_unordered=inventory.unordered + inv_adj.unordered_change,
                absolute_post_ordered=inventory.ordered + inv_adj.ordered_change,
            )
            inventory.unordered = inv_adj_log.absolute_post_unordered
            inventory.ordered = inv_adj_log.absolute_post_ordered
            inventory.save()
