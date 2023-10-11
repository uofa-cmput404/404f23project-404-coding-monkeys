# DFB pg. 165
from django.contrib.auth.models import AbstractUser
from django.db import models

class AuthorUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True) # placeholder