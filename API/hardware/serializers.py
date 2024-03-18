from rest_framework import serializers

from hardware.models import AudioData, VideoData, HardWareDevice, Text2Speech


class HardWareDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HardWareDevice
        fields = '__all__'


class AudioDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioData
        fields = '__all__'


class VideoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoData
        fields = '__all__'


class Text2SpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text2Speech
        fields = '__all__'
