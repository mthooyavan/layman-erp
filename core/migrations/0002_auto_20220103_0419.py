# Generated by Django 3.2 on 2022-01-03 04:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='type',
            new_name='product_type',
        ),
        migrations.AddField(
            model_name='order',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='error_status',
            field=models.CharField(blank=True, choices=[('stuck_in_status', 'Stuck In Status'), ('missing_inventory', 'Missing Inventory'), ('hold_requested', 'Hold Requested')], default=None, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_id',
            field=models.CharField(db_index=True, default=0, max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='warehouse',
            name='deleted_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('sku', 'name', 'product_type', 'variant')},
        ),
    ]
