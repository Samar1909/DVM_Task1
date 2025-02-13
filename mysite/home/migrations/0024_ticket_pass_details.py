# Generated by Django 5.1.5 on 2025-02-09 13:18

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0023_delete_ticket'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pass_num', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(100)])),
                ('time_booked', models.DateTimeField(default=django.utils.timezone.now)),
                ('price', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(10000)])),
                ('city1', models.CharField(max_length=50)),
                ('city2', models.CharField(max_length=50)),
                ('bus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.bus')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='pass_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(100)])),
                ('fname', models.CharField(max_length=50)),
                ('lname', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='home.ticket')),
            ],
        ),
    ]
