from rest_framework import serializers
from .models import Posts
from pages.seralizers import AuthorDetailSerializer
from static.vars import ENDPOINT

# started but needs to be finished
class LocalPostsSerializer(serializers.ModelSerializer):
    
    def get_url(self, obj):
        return f"{ENDPOINT}authors/{obj.get('author_uuid')}/posts/{obj.uuid}"

    type = serializers.CharField(default="post", max_length=6)
    id = serializers.SerializerMethodField('get_url')
    author = AuthorDetailSerializer()
    categories = serializers.ListField(default="[]")

    class Meta:
        model = Posts
        exclude = ['uuid', 'sharedWith']

class PostsSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=10, default="post")
    title = serializers.CharField(max_length=100)
    id = serializers.CharField()
    source = serializers.CharField()
    origin = serializers.CharField()
    description = serializers.CharField(max_length=300)
    contentType = serializers.CharField(max_length=20)
    content = serializers.CharField()
    author = AuthorDetailSerializer()
    categories = serializers.ListField()
    comments = serializers.CharField()
    # DateTimeField isn't JSON serializable
    published = serializers.CharField()
    visibility = serializers.CharField(max_length=10)
    unlisted = serializers.BooleanField()

class ResponsePosts(serializers.Serializer):
    type = serializers.CharField(default="posts", max_length=5)
    items = PostsSerializer(many=True)

class ImageSerializer(serializers.Serializer):
    type = serializers.CharField(default="image", max_length=5)
    data = serializers.CharField()
    contentType = serializers.CharField()

class LocalCommentSerializer(serializers.Serializer):
    author = AuthorDetailSerializer()
    comment = serializers.CharField()
    contentType = serializers.CharField(max_length=20)
    uuid = serializers.CharField()
    published = serializers.CharField()
    post_id = serializers.CharField()