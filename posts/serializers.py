from rest_framework import serializers
from .models import Posts
from pages.seralizers import AuthorUserReferenceSerializer
from static.vars import ENDPOINT

# started but needs to be finished
class PostsSerializer(serializers.ModelSerializer):
    
    def get_url(self, obj):
        return f"{ENDPOINT}authors/{obj.author.get('id')}/posts/{obj.uuid}"

    type = serializers.CharField(default="post", max_length=6)
    id = serializers.SerializerMethodField('get_url')
    author = AuthorUserReferenceSerializer()
    categories = serializers.ListField(default="[]")

    class Meta:
        model = Posts
        exclude = ['uuid', 'sharedWith']
