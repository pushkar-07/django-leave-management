# Generated by Django 5.1.4 on 2025-03-20 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0022_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bonusclaim',
            name='transaction_id',
        ),
        migrations.AddField(
            model_name='bonusclaim',
            name='original_bonus_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='bonusclaim',
            name='processed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
