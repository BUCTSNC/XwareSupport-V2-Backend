# Generated by Django 3.2 on 2021-08-25 01:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='mainProblemType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='', max_length=200)),
                ('message', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField()),
                ('Start', models.DateTimeField()),
                ('End', models.DateTimeField(blank=True, null=True)),
                ('AllowNumber', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='subProblemType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='', max_length=200)),
                ('mainType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wxapi.mainproblemtype')),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=100)),
                ('openID', models.CharField(max_length=100)),
                ('sourseInfo', models.JSONField(null=True)),
                ('problemType', models.CharField(default='', max_length=200)),
                ('describe', models.TextField()),
                ('applyTime', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.IntegerField(default=1)),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wxapi.timeslot')),
            ],
        ),
    ]
