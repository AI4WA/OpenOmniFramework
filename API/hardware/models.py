from datetime import datetime

from django.db import models

from authenticate.models import User


class Home(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=100, help_text="The name of the home", default="Blue Boat House"
    )
    address = models.CharField(
        max_length=100,
        help_text="The address of the home",
        default="1 Kings Park Ave, Crawley WA 6009",
    )

    def __str__(self):
        return f"{self.name}"


class HardWareDevice(models.Model):
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="hardware_devices",
        null=True,
        blank=True,
    )
    mac_address = models.CharField(
        max_length=100, help_text="The mac address of the hardware device", unique=True
    )
    device_name = models.CharField(
        max_length=100,
        help_text="The name of the hardware device",
        null=True,
        blank=True,
    )
    device_type = models.CharField(
        max_length=100,
        help_text="The type of the hardware device",
        null=True,
        blank=True,
    )
    description = models.TextField(
        help_text="The description of the hardware device", null=True, blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the hardware device"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the hardware device"
    )


class DataAudio(models.Model):
    home = models.ForeignKey(
        Home, on_delete=models.CASCADE, related_name="audio", null=True, blank=True
    )
    uid = models.CharField(
        max_length=100, help_text="the uid of the audio acquire session"
    )
    hardware_device_mac_address = models.CharField(
        max_length=100,
        help_text="The mac address of the hardware device",
        null=True,
        blank=True,
    )
    sequence_index = models.IntegerField(help_text="The sequence index of the audio")
    audio_file = models.CharField(max_length=100, help_text="The audio file")
    start_time = models.DateTimeField(help_text="The start time of the audio")
    end_time = models.DateTimeField(help_text="The end time of the audio")

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the audio"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the audio"
    )

    @classmethod
    def create_obj(
        cls,
        home: Home,
        uid: str,
        hardware_device_mac_address: str,
        sequence_index: int,
        audio_file: str,
        start_time: datetime,
        end_time: datetime,
    ):
        """
        Create an audio data object
        """
        return cls.objects.create(
            home=home,
            uid=uid,
            hardware_device_mac_address=hardware_device_mac_address,
            sequence_index=sequence_index,
            audio_file=audio_file,
            start_time=start_time,
            end_time=end_time,
        )

    def __str__(self):
        return f"{self.uid} - {self.audio_file}"


class DataVideo(models.Model):
    home = models.ForeignKey(
        Home, on_delete=models.CASCADE, related_name="video", null=True, blank=True
    )
    uid = models.CharField(
        max_length=100,
        help_text="the uid of the video acquire session, link back to client logs",
    )
    hardware_device_mac_address = models.CharField(
        max_length=100,
        help_text="The mac address of the hardware device",
        null=True,
        blank=True,
    )
    # TODO: add start and end time?
    video_file = models.CharField(max_length=100, help_text="The video file")
    video_record_minute = models.DateTimeField(
        help_text="The minute of the video", null=True, blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the video"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the video"
    )

    def __str__(self):
        return f"{self.uid} - {self.video_file}"


class DataText(models.Model):
    home = models.ForeignKey(
        Home, on_delete=models.CASCADE, related_name="text", null=True, blank=True
    )
    # foreign key to the audio
    audio = models.ForeignKey(
        DataAudio,
        on_delete=models.CASCADE,
        related_name="text",
        help_text="The audio data",
    )
    text = models.TextField(help_text="The text of the audio")

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the text"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the text"
    )
    model_name = models.CharField(
        max_length=100,
        help_text="The name of the model",
        null=True,
        blank=True,
        default="whisper",
    )
    pipeline_triggered = models.BooleanField(
        help_text="The pipeline is triggered or not", default=False
    )

    def __str__(self):
        return f"{self.home} - {self.text}"


class EmotionDetection(models.Model):
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="emotion_detection",
        null=True,
        blank=True,
    )
    data_text = models.ForeignKey(
        DataText,
        on_delete=models.CASCADE,
        related_name="emotion_detection",
        help_text="The text data",
    )
    result = models.JSONField(
        help_text="The emotion result of the text", null=True, blank=True, default=dict
    )
    logs = models.JSONField(
        help_text="The logs of the emotion detection",
        null=True,
        blank=True,
        default=dict,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the emotion detection"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the emotion detection"
    )


class LLMResponse(models.Model):
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="llm_response",
        null=True,
        blank=True,
    )
    data_text = models.ForeignKey(
        DataText,
        on_delete=models.CASCADE,
        related_name="llm_response",
        help_text="The text data",
    )
    messages = models.JSONField(
        help_text="The messages of the llm response",
        null=True,
        blank=True,
        default=list,
    )
    result = models.JSONField(
        help_text="The llm result of the text", null=True, blank=True, default=dict
    )
    logs = models.JSONField(
        help_text="The logs of the llm response", null=True, blank=True, default=dict
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the llm response"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the llm response"
    )


class Text2Speech(models.Model):
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="text2speech",
        null=True,
        blank=True,
    )
    data_text = models.ForeignKey(
        DataText,
        on_delete=models.SET_NULL,
        related_name="text2speech",
        help_text="The text data",
        null=True,
        blank=True,
    )
    text = models.TextField(help_text="The text of the audio", null=True, blank=True)
    text2speech_file = models.CharField(
        max_length=100, help_text="The audio file", null=True, blank=True
    )
    played = models.BooleanField(
        help_text="The audio file is played or not", default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the audio"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the audio"
    )
