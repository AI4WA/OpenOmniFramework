from rest_framework import serializers

from hardware.models import DataAudio, DataVideo, HardWareDevice, Text2Speech


class HardWareDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HardWareDevice
        fields = "__all__"


class AudioDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAudio
        fields = "__all__"


class VideoDataSerializer(serializers.ModelSerializer):
    video_record_minute = serializers.DateTimeField(
        format="%Y-%m-%d_%H-%M", input_formats=["%Y-%m-%d_%H-%M"], required=False
    )

    class Meta:
        model = DataVideo
        fields = "__all__"


class Text2SpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text2Speech
        fields = "__all__"
