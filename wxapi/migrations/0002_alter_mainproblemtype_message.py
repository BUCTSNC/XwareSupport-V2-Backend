# Generated by Django 3.2 on 2021-08-25 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wxapi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainproblemtype',
            name='message',
            field=models.TextField(blank=True, default=''),
        ),
    ]
