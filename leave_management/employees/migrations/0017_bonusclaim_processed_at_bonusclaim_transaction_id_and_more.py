# Generated by Django 5.1.4 on 2025-02-04 20:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0016_bonusclaim'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonusclaim',
            name='processed_at',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bonusclaim',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='bank_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='ifsc_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='bonusclaim',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonus_claim', to='employees.employee'),
        ),
    ]
