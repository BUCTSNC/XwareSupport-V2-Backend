from django.db import models

# Create your models here.
class User(models.Model):
    account = models.CharField(max_length=200)
    password_withSalt = models.CharField(max_length=200)
