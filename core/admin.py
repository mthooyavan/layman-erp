from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.authtoken.admin import TokenAdmin as DefaultTokenAdmin
from rest_framework.authtoken.models import Token, TokenProxy

from core import models
from utils.admin import CustomModelAdmin, EstimateCountAdminMixin, CSVActionMixin, ChoiceDropdownFilter, DropdownFilter, \
    LastMonthDateFilter, MonthYearListFilter, RelatedDropdownFilter

User = get_user_model()


class UserAdmin(DefaultUserAdmin, CustomModelAdmin):
    pass


class GroupAdmin(DefaultGroupAdmin, CustomModelAdmin):
    pass


class TokenAdmin(DefaultTokenAdmin, CustomModelAdmin):
    pass


class CustomerAdmin(CustomModelAdmin):
    """Admin class for the Customer model"""
    search_fields = ['name', 'email', 'phone']
    list_display = [
         'name', 'email', 'phone',
    ]


class ReceiptAdmin(EstimateCountAdminMixin, CSVActionMixin, CustomModelAdmin):
    search_fields = [
        'receiving_centre',
        'po_number',
    ]
    list_display = ('receiving_centre', 'po_number', 'created_at',)
    list_select_related = ['receiving_centre', 'created_by']
    list_filter = [
        ('created_at', LastMonthDateFilter),
    ]
    readonly_fields = ('created_by',)

    actions = CSVActionMixin.actions


class OrderAdmin(EstimateCountAdminMixin, CSVActionMixin, CustomModelAdmin):
    search_fields = [
        'customer__name',
        'tracking_id',
    ]
    list_display = ('tracking_sha',
                    'customer',
                    'internal_status',
                    'error_status',
                    'created_at',
                    'created_by')
    list_select_related = ['customer', 'created_by']
    list_filter = [
        ('internal_status', ChoiceDropdownFilter),
        ('error_status', ChoiceDropdownFilter),
        ('customer__name', DropdownFilter),
        ('created_at', LastMonthDateFilter),
    ]
    readonly_fields = ('created_by',)

    actions = CSVActionMixin.actions + [
        'show_related_inventory_adjustments', 'show_related_line_items',
    ]

    def show_related_inventory_adjustments(self, request, queryset):

        ids = list(queryset.values_list('id', flat=True))

        redirect_url = reverse(f'admin:{self.model._meta.app_label}_inventoryadjustment_changelist')
        redirect_url += f"?order__in={','.join(map(str, ids))}"

        return redirect(redirect_url)

    def show_related_line_items(self, request, queryset):
        ids = list(queryset.values_list('id', flat=True))

        redirect_url = reverse(f'admin:{self.model._meta.app_label}_lineitem_changelist')
        redirect_url += f"?order__in={','.join(map(str, ids))}"

        return redirect(redirect_url)


class InventoryAdmin(EstimateCountAdminMixin, CSVActionMixin, CustomModelAdmin):
    readonly_fields = (
        'unordered',
        'ordered',
        'fulfilled',
    )

    search_fields = ['product__sku', 'product__name', 'product__product_type', ]

    list_filter = [
        'product__disabled_at',
        ('product__product_type', DropdownFilter),
    ]

    list_display = (
        'product_sku', 'product_name', 'product_variant',
        'lot_code', 'uuid', 'unordered', 'ordered', 'fulfilled',
    )
    list_select_related = ['warehouse', 'product']

    actions = CSVActionMixin.actions + ['show_adjustment_logs', ]

    # pylint: disable=no-self-use
    def product_name(self, obj):
        return obj.product.name

    product_name.admin_order_field = 'product__name'
    product_name.short_description = 'Product'

    # pylint: disable=no-self-use
    def product_variant(self, obj):
        return obj.product.variant

    product_variant.admin_order_field = 'product__variant'
    product_variant.short_description = 'Variant'

    # pylint: disable=no-self-use
    def product_sku(self, obj):
        return obj.product.sku

    product_sku.admin_order_field = 'product__sku'
    product_sku.short_description = 'SKU'

    # pylint: disable=no-self-use
    def show_adjustment_logs(self, request, queryset):
        ids = list(queryset.values_list('id', flat=True))

        redirect_url = reverse(f'admin:{self.model._meta.app_label}_inventoryadjustmentlog_changelist')
        redirect_url += f"?inventory__in={','.join(map(str, ids))}"

        return redirect(redirect_url)


class InventoryAdjustmentAdmin(EstimateCountAdminMixin, CSVActionMixin, CustomModelAdmin):
    search_fields = ['inventory__product__name', 'inventory__product__sku']
    list_display = ('__str__', 'unordered_change', 'ordered_change', 'fulfilled_change',
                    'order_tracking_id', 'reason', 'created_by', 'created_at',)

    list_select_related = (
        'order', 'user', 'inventory', 'inventory__product', 'inventory__warehouse',
    )

    list_filter = [
        ('reason', ChoiceDropdownFilter),
        ('inventory__warehouse__short_code', DropdownFilter),
        ('inventory__warehouse__name', DropdownFilter),
        ('user__username', DropdownFilter),
        ('created_at', MonthYearListFilter),
    ]

    readonly_fields = (
        'order_id',
        'created_at',
    )

    actions = CSVActionMixin.actions + ['show_adjustment_logs']

    # pylint: disable=no-self-use
    def order_tracking_id(self, inventory_adjustment):
        order = inventory_adjustment.order
        if order:
            return order.tracking_id
        return ''

    order_tracking_id.admin_order_field = 'order__tracking_id'
    order_tracking_id.short_description = 'Order'

    # pylint: disable=no-self-use
    def created_by(self, inventory_adjustment):
        user = inventory_adjustment.user
        if user:
            return user.username
        return ''

    created_by.admin_order_field = 'user__username'
    created_by.short_description = 'Created By'

    # pylint: disable=no-self-use
    def show_adjustment_logs(self, request, queryset):
        ids = list(queryset.values_list('id', flat=True))

        redirect_url = reverse(f'admin:{self.model._meta.app_label}_inventoryadjustmentlog_changelist')
        redirect_url += f"?source_adjustment__in={','.join(map(str, ids))}"

        return redirect(redirect_url)


# pylint: disable=no-self-use
class InventoryAdjustmentLogAdmin(EstimateCountAdminMixin, CSVActionMixin, CustomModelAdmin):
    search_fields = [
        'inventory__product__name', 'inventory__product__sku',
        'source_adjustment__reason', 'source_adjustment__order__tracking_id'
    ]

    list_display = ['created_at', 'product_name', 'product_sku',
                    'warehouse', 'reason', 'created_by',
                    'unordered_change', 'ordered_change', 'fulfilled_change',
                    'absolute_pre_unordered', 'absolute_post_unordered',
                    'absolute_pre_ordered', 'absolute_post_ordered',
                    'absolute_pre_fulfilled', 'absolute_post_fulfilled',
                    'order_tracking_id']

    list_download = list_display + ['source_adjustment__inventory__product__name',
                                    'source_adjustment__inventory__product__sku',
                                    'source_adjustment__unordered_change',
                                    'source_adjustment__ordered_change',
                                    'source_adjustment__fulfilled_change']

    list_select_related = (
        'inventory', 'inventory__product', 'inventory__warehouse',
        'source_adjustment', 'source_adjustment__user', 'source_adjustment__order'
    )

    list_filter = [
        ('source_adjustment__reason', ChoiceDropdownFilter),
        ('inventory__warehouse__short_code', RelatedDropdownFilter),
        ('created_at', MonthYearListFilter),
    ]

    readonly_fields = (
        'unordered_change',
        'ordered_change',
        'fulfilled_change',
        'absolute_pre_unordered',
        'absolute_pre_ordered',
        'absolute_pre_fulfilled',
        'absolute_post_unordered',
        'absolute_post_ordered',
        'absolute_post_fulfilled',
    )

    def product_name(self, obj):
        return obj.inventory.product.name if obj.inventory.product else None

    def product_sku(self, obj):
        return obj.inventory.product.sku if obj.inventory.product else None

    def reason(self, obj):
        return obj.source_adjustment.reason if obj.source_adjustment else None

    def source_adjustment_unordered_change(self, obj):
        return obj.source_adjustment.unordered_change if obj.source_adjustment else None

    def source_adjustment_ordered_change(self, obj):
        return obj.source_adjustment.ordered_change if obj.source_adjustment else None

    def source_adjustment_fulfilled_change(self, obj):
        return obj.source_adjustment.fulfilled_change if obj.source_adjustment else None

    def created_by(self, obj):
        return obj.source_adjustment.user.username if obj.source_adjustment.user else None

    def order_tracking_id(self, obj):
        return obj.source_adjustment.order.tracking_id if obj.source_adjustment.order else None

    def warehouse(self, obj):
        return obj.inventory.warehouse.short_code


# pylint: disable=no-self-use
class ProductAdmin(CSVActionMixin, CustomModelAdmin):
    search_fields = ['sku', 'name', ]
    list_filter = [
        'disabled_at', 'variant'
    ]
    list_display = ('name', 'sku', 'variant', 'product_type',)

    list_download = list_display

    actions = CSVActionMixin.actions


class LineItemAdmin(EstimateCountAdminMixin, CSVActionMixin, CustomModelAdmin):
    search_fields = ('product__sku', 'product__name',
                     'uuid', 'order__tracking_id')
    list_display = ('order_tracking_id', 'product', 'price', 'quantity')
    list_select_related = ('order', 'product',)
    list_filter = [('product__product_type', DropdownFilter)]


class LocationAdmin(CSVActionMixin, CustomModelAdmin):
    list_display = ('label', 'aisle', 'column', 'level',)
    search_fields = ['label', 'aisle', 'column', 'level', 'warehouse']
    list_filter = [
        ('warehouse__short_code', DropdownFilter)
    ]
    list_select_related = ('warehouse', )


class LotCodeAdmin(CSVActionMixin, CustomModelAdmin):
    list_display = ['product', 'lot_number', ]
    search_fields = ['product__sku', 'product__name', ]
    list_filter = [('product__product_type', DropdownFilter)]
    list_select_related = ['product']


class WarehouseAdmin(EstimateCountAdminMixin, CSVActionMixin, CustomModelAdmin):
    search_fields = ['name', 'description', 'address_1',
                     'address_2', 'zip_code', 'city']
    list_display = ('name', 'description', 'city', 'deleted_at')
    list_filter = [('deleted_at', MonthYearListFilter)]
    readonly_fields = ['name', 'description']


# Register your models here.
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Token, TokenAdmin)

admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.Inventory, InventoryAdmin)
admin.site.register(models.InventoryAdjustmentLog, InventoryAdjustmentLogAdmin)
admin.site.register(models.InventoryAdjustment, InventoryAdjustmentAdmin)
admin.site.register(models.LineItem, LineItemAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.LotCode, LotCodeAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Warehouse, WarehouseAdmin)
