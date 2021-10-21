from collections import namedtuple
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class DfType(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=25)

class pIndicator(models.Model):
    formula = models.CharField(max_length=300)
    name = models.CharField(max_length=100)
    valueType = models.CharField(max_length=100, default="abs")

class Data(models.Model):
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=False)
    dfCode = models.ForeignKey(DfType, on_delete=models.PROTECT)
    value = models.DecimalField(decimal_places=2, max_digits=12)
    country = models.CharField(max_length=100, default="Germany")

class Dashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    index = models.IntegerField()
    data = models.CharField(max_length=100)
    type = models.IntegerField() # 0: DF; 1: KPI
    market = models.CharField(max_length=100)