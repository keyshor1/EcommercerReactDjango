# Generated by Django 5.0.4 on 2024-06-10 15:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_cart'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_name', models.CharField(max_length=255)),
                ('receiver_name', models.CharField(max_length=255)),
                ('receiver_email', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=250)),
                ('city', models.CharField(max_length=250)),
                ('locality', models.CharField(max_length=250)),
                ('sender_number', models.TextField(default='')),
                ('receiver_number', models.TextField(default='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]