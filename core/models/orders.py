from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from model_utils import Choices

from utils.models import CustomModel

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


class Order(CustomModel):
    customer = models.ForeignKey(
        'Customer', on_delete=models.PROTECT,
        related_name='orders'
    )
    internal_status = models.CharField(
        max_length=20,
        choices=INTERNAL_STATUS_CHOICES,
        default=INTERNAL_STATUS_CHOICES.not_yet_picked, db_index=True
    )
    print_priority = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Set the priority for this order to be packed - 1 is the highest priority, 10 is the lowest'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
