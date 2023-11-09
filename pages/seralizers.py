from rest_framework import serializers
from accounts.models import AuthorUser
from static.vars import ENDPOINT

class AuthorUserSerializer(serializers.ModelSerializer):
    
    def get_url(self, obj):
        return f"{ENDPOINT}authors/{obj.get('uuid')}"

    type = serializers.CharField(default="author", max_length=6)
    id = serializers.SerializerMethodField('get_url')
    displayName = serializers.CharField(max_length=100, source='username')
    profileImage = serializers.CharField(max_length=100, source='profile_image')

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

class AuthorUserReferenceSerializer(serializers.Serializer):
    type = serializers.CharField(default="author", max_length=6)
    id = serializers.CharField()
    url = serializers.CharField()
    host = serializers.CharField()
    github = serializers.CharField()
    displayName = serializers.CharField(max_length=50)
    profileImage = serializers.CharField()


class FollowerSerializer(serializers.Serializer):
    
    type = serializers.CharField(default="author", max_length=6)
    id = serializers.CharField(max_length=100)
    host = serializers.CharField(max_length=100)
    displayName = serializers.CharField(max_length=100, source='username')
    url = serializers.CharField(max_length=100)
    github = serializers.CharField(max_length=100)
    profileImage = serializers.CharField(max_length=100, source='profile_image')


class FollowerListSerializer(serializers.Serializer):
    class Meta:
        model = AuthorUser
        fields = ['author','followers']

    author = AuthorUserSerializer()
    followers = FollowerSerializer(many=True)

    def update(self, instance, validated_data):
        instance.author = validated_data.get('author', instance.author)
        instance.followers = validated_data.get('followers', instance.followers)
        instance.save()
        return instance

class FollowRequestsSerializer(serializers.Serializer):
    type = serializers.CharField(default="Follow", max_length=10)
    summary = serializers.CharField()
    actor = AuthorUserSerializer()
    object = AuthorUserSerializer()