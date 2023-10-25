# DFB pg. 165
from django.contrib.auth.models import AbstractUser
from django.db import models

class AuthorUser(AbstractUser):
    #id - should be generated by db automatically
    type = models.CharField(default="author",max_length=6)
    username = models.CharField(max_length=20, unique=True) # https://www.reddit.com/r/django/comments/id2ch0/user_models_username_max_length/
    host = models.GenericIPAddressField(default = "http://127.0.0.1:8000/") # hardcoded localhost for now
    url = models.URLField() #TODO setup proper page
    github = models.URLField(null=True, blank=True)
    profile_image = models.URLField(null=True, blank=True) # optional

class Followers(models.Model):
    author = models.ForeignKey(AuthorUser, on_delete=models.CASCADE, related_name='author')
    followers = models.JSONField(default=list)

    def __str__(self): # show summary in django admin view tooltip 
        return self.author.username + "'s " + "Followers"

# This table will delete requests once they have been fulfilled and added to the Follower table
class FollowRequests(models.Model):
    summary = models.CharField(max_length=100)
    # could possible have a boolean for requester and recipient to see if they are local to our node, and instead
    # of storing an entire dictionary of information it can just be an author id which we will retrieve data from in
    # the AuthorUser table. Will see.
    requester = models.JSONField(default=dict)
    recipient = models.JSONField(default=dict)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): # show summary in django admin view tooltip 
        return self.summary

    # can only request somebody once
    class Meta:
        unique_together = ('requester', 'recipient')