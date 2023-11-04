from rest_framework import serializers
from accounts.models import Posts
from pages.seralizers import AuthorSerializer

class PostsSerializer(serializers.ModelSerializer):
    
    type = serializers.CharField(default="posts", max_length=6)
    author = AuthorSerializer()

    class Meta:
        model = Posts
