# Generated by Django 4.2.10 on 2024-05-11 18:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthlypayment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='monthly_payments', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
