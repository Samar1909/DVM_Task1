# Generated by Django 5.1.5 on 2025-02-18 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_ticket_email_otp_alter_myuser_email_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='email_otp',
            field=models.CharField(blank=True, default=None, max_length=6, null=True),
        ),
    ]
