from django.db import models
from accounts.models import AuthorUser

# Create your models here.
class Inbox(models.Model):
    author = models.ForeignKey(AuthorUser, on_delete=models.CASCADE, to_field="uuid")
    items = models.JSONField(default=list)
