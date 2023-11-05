from rest_framework import serializers
from accounts.models import Posts
from pages.seralizers import AuthorSerializer

# started but needs to be finished
class PostsSerializer(serializers.ModelSerializer):
    
    type = serializers.CharField(default="posts", max_length=6)
    author = AuthorSerializer()

    class Meta:
        model = Posts
