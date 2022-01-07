from django.db import models


class InventoryAdjustmentLog(models.Model):
    inventory = models.ForeignKey('Inventory', on_delete=models.PROTECT,
                                  null=True, blank=True)

    source_adjustment = models.ForeignKey('InventoryAdjustment', on_delete=models.PROTECT)

    unordered_change = models.IntegerField(default=0)
    ordered_change = models.IntegerField(default=0)

    absolute_pre_unordered = models.IntegerField(default=0)
    absolute_pre_ordered = models.IntegerField(default=0)

    absolute_post_unordered = models.IntegerField(default=0)
    absolute_post_ordered = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"InvAdjLog: {self.inventory}: unordered change: {self.unordered_change}"
