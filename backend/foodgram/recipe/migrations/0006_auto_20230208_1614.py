# Generated by Django 2.2.16 on 2023-02-08 13:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0005_auto_20230208_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredientinrecipe',
            name='counts',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='counts',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=False,
        ),
    ]
