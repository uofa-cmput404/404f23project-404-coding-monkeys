from rest_framework import serializers
from accounts.models import AuthorUser
from static.vars import ENDPOINT

class AuthorUserSerializer(serializers.ModelSerializer):
    
    def get_url(self, obj):
        return f"{ENDPOINT}authors/{obj.uuid}"

    type = serializers.CharField(default="author", max_length=6)
    id = serializers.SerializerMethodField('get_url')
    displayName = serializers.CharField(source='username')
    profileImage = serializers.CharField(source='profile_image')

    class Meta:
        model = AuthorUser
        fields = ['type', 'id', 'host', 'displayName', "url", 'github', 'profileImage']

    def update(self, instance, validated_data):
        instance.host = validated_data.get('host', instance.host)
        instance.username = validated_data.get('username', instance.username)
        instance.url = validated_data.get('url', instance.url)
        instance.github = validated_data.get('github', instance.github)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance

class AuthorDetailSerializer(serializers.Serializer):
    type = serializers.CharField(default="author", max_length=6)
    id = serializers.CharField(max_length=300)
    url = serializers.CharField(max_length=300)
    host = serializers.CharField(max_length=300)
    github = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    displayName = serializers.CharField(max_length=100)
    profileImage = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class ResponseAuthorsSerializer(serializers.Serializer):
    type = serializers.CharField(default="authors", max_length=7)
    items = AuthorUserSerializer(many=True)

class ResponseFollowersSerializer(serializers.Serializer):
    type = serializers.CharField(default="followers", max_length=9)
    items = AuthorUserSerializer(many=True)

class FollowerListSerializer(serializers.Serializer):
    class Meta:
        model = AuthorUser
        fields = ['author','followers']

    author = AuthorUserSerializer()
    followers = AuthorUserSerializer(many=True)

    def update(self, instance, validated_data):
        instance.author = validated_data.get('author', instance.author)
        instance.followers = validated_data.get('followers', instance.followers)
        instance.save()
        return instance

class FollowRequestsSerializer(serializers.Serializer):
    type = serializers.CharField(default="Follow", max_length=10)
    summary = serializers.CharField()
    actor = AuthorDetailSerializer()
    object = AuthorDetailSerializer()

# the reference serializers are expecting properly formatted input from server responses and act as 
# the "template" for the request data (1:1 with what is in spec)

class AuthorUserSerializerDB(serializers.Serializer):
    type = serializers.CharField(default="author", max_length=6)
    id = serializers.CharField()
    url = serializers.CharField()
    host = serializers.CharField()
    github = serializers.CharField()
    username = serializers.CharField(max_length=50, source='displayName')
    profile_image = serializers.CharField(source='profileImage')

class AuthorUserReferenceSerializer(serializers.Serializer):
    type = serializers.CharField(default="author", max_length=6)
    id = serializers.CharField()
    url = serializers.CharField()
    host = serializers.CharField()
    github = serializers.CharField()
    displayName = serializers.CharField(max_length=50)
    profileImage = serializers.CharField()

class LikeSerializer(serializers.Serializer):
    context = serializers.CharField()
    summary = serializers.CharField()
    type = serializers.CharField(default="like", max_length=4)
    author = AuthorDetailSerializer()
    object = serializers.CharField()

class CommentSerializer(serializers.Serializer):
    type = serializers.CharField(default="comment", max_length=7)
    author = AuthorDetailSerializer()
    comment = serializers.CharField()
    contentType = serializers.CharField(max_length=20)
    published = serializers.CharField()
    id = serializers.CharField()

class CommentListSerializer(serializers.Serializer):
    type = serializers.CharField(default="comments", max_length=8)
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    post = serializers.CharField()
    comments = CommentSerializer(many=True)
    id = serializers.CharField()