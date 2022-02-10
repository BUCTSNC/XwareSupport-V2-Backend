from django.db import models
from wxapi import models as md

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=200,unique=True,null=False)
    passwordHashWithSalt = models.CharField(max_length=1000)
    salt = models.CharField(max_length=200)
    nickname = models.CharField(max_length=200,default="")
    auth = models.IntegerField(default=0)
    status = models.IntegerField(default=1)

class DealAppointment(models.Model):
    manage_username = models.ForeignKey(User, on_delete=models.CASCADE,to_field="username",default="null")
    appointment_uuid = models.ForeignKey(md.Appointment, on_delete=models.CASCADE,to_field="uuid")
    status = models.IntegerField(default=1)

class SummaryAppointment(models.Model):
    imgurl = models.CharField(max_length=500)
    problem = models.CharField(max_length=200)
    problemType = models.CharField(max_length=20)
    inspection = models.CharField(max_length=200)
    processAndWays = models.CharField(max_length=200)
    finalEffect = models.CharField(max_length=100)
    companions = models.CharField(max_length=30)
    manage_username = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username", default="null")
    appointment_uuid = models.ForeignKey(md.Appointment, on_delete=models.CASCADE, to_field="uuid")
    pcbrand = models.CharField(max_length=30,default="")
    pcmodel = models.CharField(max_length=30,default="")

