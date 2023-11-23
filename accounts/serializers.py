from rest_framework import serializers

class TokenSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    username = serializers.CharField()
    host = serializers.CharField()
    url = serializers.CharField()