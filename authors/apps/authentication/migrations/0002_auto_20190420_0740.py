# Generated by Django 2.1.4 on 2019-04-20 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='in_app_notifications',
            field=models.BooleanField(default=True),
        ),
    ]
