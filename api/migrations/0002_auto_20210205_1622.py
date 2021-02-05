# Generated by Django 3.1.6 on 2021-02-05 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='mobile',
            field=models.CharField(max_length=13, unique=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='otp_expire',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
