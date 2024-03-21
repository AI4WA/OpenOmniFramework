from datetime import datetime

from django.db import models


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
                   hardware_device_mac_address: str,
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
            hardware_device_mac_address=hardware_device_mac_address,
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
    video_record_minute = models.DateTimeField(help_text="The minute of the video", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="The created time of the video")
    updated_at = models.DateTimeField(auto_now=True, help_text="The updated time of the video")

    class Meta:
        db_table = 'video_data'

    def __str__(self):
        return f"{self.uid} {self.video_file}"


class ReactionToAudio(models.Model):
    audio = models.OneToOneField(AudioData,
                                 on_delete=models.SET_NULL,
                                 related_name='reaction',
                                 null=True,
                                 blank=True,
                                 help_text="The audio data")
    react_already = models.BooleanField(help_text="The audio data has been reacted or not", default=False)
    emotion_result = models.JSONField(help_text="The emotion result of the audio", null=True, blank=True)
    failed = models.BooleanField(help_text="The reaction failed or not", default=False)
    failed_reason = models.TextField(help_text="The reason of the reaction failed", null=True, blank=True)
    llm_response = models.JSONField(help_text="The llm response of the audio", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="The created time of the reaction")
    updated_at = models.DateTimeField(auto_now=True, help_text="The updated time of the reaction")


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
