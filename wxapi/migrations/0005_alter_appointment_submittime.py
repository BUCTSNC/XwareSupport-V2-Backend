# Generated by Django 3.2.7 on 2021-10-04 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wxapi', '0004_appointment_submittime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='submitTime',
            field=models.CharField(max_length=50),
        ),
    ]
