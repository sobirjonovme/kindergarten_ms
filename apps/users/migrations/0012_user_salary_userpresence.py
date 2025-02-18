# Generated by Django 4.2.10 on 2024-06-09 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_user_face_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='salary',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=13, null=True, verbose_name='Salary'),
        ),
        migrations.CreateModel(
            name='UserPresence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('enter_at', models.DateTimeField(blank=True, null=True, verbose_name='Enter at')),
                ('exit_at', models.DateTimeField(blank=True, null=True, verbose_name='Exit at')),
                ('present_time', models.PositiveIntegerField(default=0, help_text='in hours', verbose_name='Present Time')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Presence',
                'verbose_name_plural': 'User Presences',
            },
        ),
    ]
