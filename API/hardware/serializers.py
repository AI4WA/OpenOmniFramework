from rest_framework import serializers

from hardware.models import AudioData, VideoData


class AudioDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioData
        fields = '__all__'


class VideoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoData
        fields = '__all__'
