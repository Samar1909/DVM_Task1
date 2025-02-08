# Generated by Django 5.1.5 on 2025-02-08 14:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_alter_bus_bus_number_alter_bus_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='bus_number',
            field=models.IntegerField(default=None, null=True, validators=[django.core.validators.MaxValueValidator(99999), django.core.validators.MinValueValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='bus',
            name='name',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bus',
            name='time_end',
            field=models.CharField(default=None, max_length=4, null=True, validators=[django.core.validators.RegexValidator('^([01]\\d|2[0-3])([0-5]\\d)$', 'Enter a valid time in 24 hour format')]),
        ),
        migrations.AlterField(
            model_name='bus',
            name='time_start',
            field=models.CharField(default=None, max_length=4, null=True, validators=[django.core.validators.RegexValidator('^([01]\\d|2[0-3])([0-5]\\d)$', 'Enter a valid time in 24 hour format')]),
        ),
    ]
