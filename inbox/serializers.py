from rest_framework import serializers
from .models import Inbox
from accounts.models import AuthorUser
from pages.seralizers import AuthorUserSerializer, AuthorUserReferenceSerializer, AuthorUserSerializerDB
from static.vars import ENDPOINT


class InboxItemSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=10)
    title = serializers.CharField(max_length=100)
    id = serializers.CharField()
    source = serializers.CharField()
    origin = serializers.CharField()
    description = serializers.CharField(max_length=300)
    contentType = serializers.CharField(max_length=20)
    content = serializers.CharField()
    author = AuthorUserSerializer()
    categories = serializers.ListField()
    comments = serializers.CharField()
    # DateTimeField isn't JSON serializable
    published = serializers.CharField()
    visibility = serializers.CharField(max_length=10)
    unlisted = serializers.BooleanField()


class InboxSerializer(serializers.Serializer):
    class Meta:
        model = Inbox
        fields = ['type', 'author','items']

    def get_url(self, obj):
        return f"{ENDPOINT}authors/{obj.author_id}"

    type = serializers.CharField(default="inbox",max_length=6)
    author = serializers.SerializerMethodField('get_url')
    items = InboxItemSerializer(many=True)

    def update(self, instance, validated_data):
        # instance.author = validated_data.get('author', instance.author)
        instance.items = validated_data.get('items', instance.followers)
        instance.save()
        return instance

