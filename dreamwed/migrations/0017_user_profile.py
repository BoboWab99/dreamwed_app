# Generated by Django 3.2.6 on 2021-09-11 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dreamwed', '0016_auto_20210827_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile',
            field=models.ImageField(default='default.jpg', upload_to='profile_pics'),
        ),
    ]
