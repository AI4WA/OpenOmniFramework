from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from hardware.models import AudioData
from hardware.serializers import AudioDataSerializer


class AudioDataViewSet(viewsets.ModelViewSet):
    queryset = AudioData.objects.all()
    serializer_class = AudioDataSerializer
