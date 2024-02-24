from rest_framework import serializers
from hardware.models import AudioData


class AudioDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioData
        fields = '__all__'
