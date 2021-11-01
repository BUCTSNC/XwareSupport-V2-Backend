from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=200)
    passwordHashWithSalt = models.CharField(max_length=1000)
    salt = models.CharField(max_length=200)
    nickname = models.CharField(max_length=200,default="")
    auth = models.IntegerField(default=0)
    status = models.IntegerField(default=1)

