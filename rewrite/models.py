from django.db import models


class APICounter(models.Model):
    count = models.IntegerField(default=0)
