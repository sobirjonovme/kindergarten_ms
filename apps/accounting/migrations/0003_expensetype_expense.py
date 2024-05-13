# Generated by Django 4.2.10 on 2024-05-13 04:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_alter_monthlypayment_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=127, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Expense Type',
                'verbose_name_plural': 'Expense Types',
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=13, verbose_name='Amount')),
                ('paid_date', models.DateField(default=django.utils.timezone.now, verbose_name='Paid Date')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='accounting.expensetype', verbose_name='Type')),
            ],
            options={
                'verbose_name': 'Expense',
                'verbose_name_plural': 'Expenses',
            },
        ),
    ]
