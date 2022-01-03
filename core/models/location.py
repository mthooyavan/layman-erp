import uuid
from typing import Optional

from django.db import models

from utils.models import CustomModel


class Location(CustomModel):
    class Meta:
        unique_together = ('warehouse', 'aisle', 'column', 'level',)

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    label = models.CharField(
        max_length=128 + 4, blank=True, null=True,
        help_text='Can be set generically, or will be calculated if any of the aisle, column, level, bin are set.'
    )

    aisle = models.CharField(max_length=32, blank=True, null=True)
    column = models.CharField(max_length=32, blank=True, null=True)
    level = models.CharField(max_length=32, blank=True, null=True)

    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    enabled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self._get_label()
        super().save(*args, **kwargs)

    def _get_label(self) -> Optional[str]:
        separator = ' '
        label_components = [self.aisle, self.column, self.level]
        if any(label_components):
            return separator.join(filter(None, label_components))
        return None

    def __str__(self) -> str:
        return self.label
