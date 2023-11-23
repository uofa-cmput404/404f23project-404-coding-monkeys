from django.db import models
import datetime

from accounts.models import AuthorUser

class Posts(models.Model):
    title = models.CharField(max_length=100)
    # do we want ID as entire URL or just post id?
    uuid = models.CharField(primary_key=True, unique=True, max_length=36)
    source = models.URLField()
    origin = models.URLField()
    description = models.CharField(max_length=200)
    # The content type of the post, one of:
    # text/markdown -- common mark
    # text/plain -- UTF-8
    # application/base64
    # image/png;base64 # this is an embedded png -- images are POSTS. So you might have a user make 2 posts if a post includes an image!
    # image/jpeg;base64 # this is an embedded jpeg
    contentType = models.CharField(max_length=100)
    content = models.TextField()
    author_uuid = models.CharField(max_length=36)
    author_local = models.BooleanField(default=False)
    author_url = models.CharField(max_length=100, null=True)
    author_host = models.CharField(max_length=100, null=True)
    # categories this post fits into (a list of strings
    categories = models.JSONField(default=list)
    # total number of comments for this post
    likeCount = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    comments = models.URLField()
    # commentsSrc is OPTIONAL to reduce API call counts
    # You should return ~ 5 comments per post.
    # should be sorted newest(first) to oldest(last)
    commentsSrc = models.JSONField(default=dict)
    published = models.DateTimeField(auto_now_add=True, null=True)
    # one of ["PUBLIC","FRIENDS"]
    VISIBILITY_OPTIONS = [('PUBLIC', 'Public'), ('FRIENDS', 'Friends-Only'), ('PRIVATE', 'Private')]
    visibility = models.CharField(max_length=10, choices=VISIBILITY_OPTIONS)
    # will contain author information for who its shared with if the visibility is PRIVATE, null otherwise
    sharedWith = models.JSONField(default=list, null=True)
    # unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
    unlisted = models.BooleanField(default=False)

# before saving a like we will have to check if the originating post is open to PUBLIC or FRIENDS
class Likes(models.Model):
    # TODO: Should we have a field type = "like"?
    context = models.URLField()
    summary = models.CharField(max_length=100)
    # when searching for public things an author has liked, we will filter by author
    author_uuid = models.CharField(max_length=36)
    author_host = models.CharField(max_length=100, null=True)
    author_url = models.CharField(max_length=100, null=True)
    # liked_object can either be a post or a comment; when searching for the number of likes / who has liked a post or comment, 
    # we will filter by liked_object
    liked_id = models.CharField(max_length=36)
    liked_object = models.URLField()
    LIKE_OBJECTS = [('post', 'Post'), ('comment', 'Comment')]
    liked_object_type = models.CharField(max_length=10, choices=LIKE_OBJECTS)

# TODO deduce pagination on a case by case basis, on request
class Comments(models.Model):
    # would UUIDs be better as links or just the UUID?
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uuid = models.CharField(primary_key=True, unique=True, max_length=36)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='post', to_field="uuid")
    author_uuid = models.CharField(max_length=36)
    author_host = models.CharField(max_length=100, null=True)
    author_url = models.CharField(max_length=100, null=True)
    comment = models.TextField()
    contentType = models.CharField(max_length=100)
    published = models.DateTimeField(auto_now_add=True)
