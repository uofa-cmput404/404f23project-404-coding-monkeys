from django.db import models


# Create your models here.
class Node(models.Model):
    index = models.IntegerField()
    host = models.URLField()
    username = models.CharField(max_length=50)
    password = models.BinaryField(max_length=200)
