from rest_framework import serializers
from accounts.models import AuthorUser

class AuthorUserSerializer(serializers.Serializer):
    type = serializers.CharField(default="author", max_length=6)
    id = serializers.CharField(max_length=100)
    host = serializers.CharField(max_length=100)
    displayName = serializers.CharField(max_length=100, source='username')
    url = serializers.CharField(max_length=100)
    github = serializers.CharField(max_length=100)
    profileImage = serializers.CharField(max_length=100, source='profile_image')

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.host = validated_data.get('host', instance.host)
        instance.username = validated_data.get('displayName', instance.username)
        instance.url = validated_data.get('url', instance.url)
        instance.github = validated_data.get('github', instance.github)
        instance.profile_image = validated_data.get('profileImage', instance.profile_image)
        instance.save()
        return instance

