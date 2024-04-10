from rest_framework import serializers


class RespondToChatSerializer(serializers.Serializer):
    chat_uuid = serializers.UUIDField()
    message = serializers.CharField()
