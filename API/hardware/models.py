from django.db import models
from datetime import datetime


class HardWareDevice(models.Model):
    mac_address = models.CharField(max_length=100,
                                   help_text="The mac address of the hardware device",
                                   unique=True)
    device_name = models.CharField(max_length=100, help_text="The name of the hardware device", null=True, blank=True)
    device_type = models.CharField(max_length=100, help_text="The type of the hardware device", null=True, blank=True)
    description = models.TextField(help_text="The description of the hardware device", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="The created time of the hardware device")
    updated_at = models.DateTimeField(auto_now=True, help_text="The updated time of the hardware device")


class AudioData(models.Model):
    uid = models.CharField(max_length=100)
    hardware_device_mac_address = models.CharField(max_length=100, help_text="The mac address of the hardware device",
                                                   null=True, blank=True)
    sequence_index = models.IntegerField(help_text="The sequence index of the audio")
    text = models.TextField(help_text="The text of the audio")
    audio_file = models.CharField(max_length=100, help_text="The audio file")
    start_time = models.DateTimeField(help_text="The start time of the audio")
    end_time = models.DateTimeField(help_text="The end time of the audio")
    translation_in_seconds = models.FloatField(help_text="The time taken to translate the audio")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The created time of the audio")
    updated_at = models.DateTimeField(auto_now=True, help_text="The updated time of the audio")

    class Meta:
        db_table = 'audio_data'
        unique_together = ('uid', 'sequence_index')

    def __str__(self):
        return f"{self.uid} {self.sequence_index} {self.text}"

    @classmethod
    def create_obj(cls,
                   uid: str,
                   sequence_index: int,
                   text: str,
                   audio_file: str,
                   translation_in_seconds: float,
                   start_time: datetime,
                   end_time: datetime

                   ):
        """
        Create an audio data object
        """
        return cls.objects.create(
            uid=uid,
            sequence_index=sequence_index,
            text=text,
            audio_file=audio_file,
            translation_in_seconds=translation_in_seconds,
            start_time=start_time,
            end_time=end_time
        )


class VideoData(models.Model):
    uid = models.CharField(max_length=100)
    hardware_device_mac_address = models.CharField(max_length=100, help_text="The mac address of the hardware device",
                                                   null=True, blank=True)
    video_file = models.CharField(max_length=100, help_text="The video file")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The created time of the video")
    updated_at = models.DateTimeField(auto_now=True, help_text="The updated time of the video")

    class Meta:
        db_table = 'video_data'

    def __str__(self):
        return f"{self.uid} {self.video_file}"


class Text2Speech(models.Model):
    hardware_device_mac_address = models.CharField(max_length=100, help_text="The mac address of the hardware device",
                                                   null=True, blank=True)
    text = models.TextField(help_text="The text of the audio", null=True, blank=True)
    audio_file = models.CharField(max_length=100, help_text="The audio file", null=True, blank=True)
    spoken = models.BooleanField(help_text="The audio file is spoken or not", default=False)
    created_at = models.DateTimeField(auto_now_add=True, help_text="The created time of the audio")
    updated_at = models.DateTimeField(auto_now=True, help_text="The updated time of the audio")

    class Meta:
        db_table = 'text2speech'

    def __str__(self):
        return f"{self.text} {self.hardware_device_mac_address}"
