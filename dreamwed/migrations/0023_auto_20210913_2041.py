# Generated by Django 3.2.6 on 2021-09-13 17:41

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dreamwed', '0022_auto_20210912_1739'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['modified', 'created']},
        ),
        migrations.RemoveField(
            model_name='review',
            name='date_posted',
        ),
        migrations.AddField(
            model_name='review',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='stars',
            field=models.PositiveSmallIntegerField(default=5, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)]),
        ),
    ]
