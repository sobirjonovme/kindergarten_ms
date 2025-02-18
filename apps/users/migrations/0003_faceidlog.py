# Generated by Django 4.2.10 on 2024-05-08 16:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_educating_group_user_middle_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaceIDLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Face ID Log',
                'verbose_name_plural': 'Face ID Logs',
            },
        ),
    ]
