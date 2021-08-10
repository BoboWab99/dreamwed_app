# Generated by Django 3.2.6 on 2021-08-08 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dreamwed', '0006_auto_20210807_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetitem',
            name='cost',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='budgetitem',
            name='paid',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='todo',
            name='cost',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='todo',
            name='due_date',
            field=models.DateTimeField(blank=True, help_text='When would you like to have this done?', null=True),
        ),
        migrations.AlterField(
            model_name='weddingplanner',
            name='wedding_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
