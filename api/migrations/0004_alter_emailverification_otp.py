# Generated by Django 5.1 on 2024-08-17 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_emailverification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverification',
            name='otp',
            field=models.CharField(max_length=4, unique=True),
        ),
    ]