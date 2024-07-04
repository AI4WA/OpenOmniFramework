from datetime import datetime

from django.db import models

from authenticate.models import User


class Home(models.Model):
    """
    Created by setup manually, and the client side can specify the home, so all data will be connected to this.
    """

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
    """
    One home can have multiple hardware devices, and the hardware device can be used to acquire the audio and video data

    """

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

    class Meta:
        verbose_name = "Hardware Device"
        verbose_name_plural = "Hardware Devices"


class DataAudio(models.Model):
    """
    Link to home and hardware device, and the audio data will be stored in the database
    It will be created by the endpoint from client side when audio data is acquired
    """

    home = models.ForeignKey(
        Home, on_delete=models.CASCADE, related_name="audio", null=True, blank=True
    )
    hardware_device_mac_address = models.CharField(
        max_length=100,
        help_text="The mac address of the hardware device",
        null=True,
        blank=True,
    )
    uid = models.CharField(
        max_length=100,
        help_text="the uid of the audio acquire session, can be treated as scenario id",
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
    track_id = models.CharField(
        max_length=100,
        help_text="The track id of the multimodal conversation",
        null=True,
        blank=True,
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
        track_id: str = None,
    ):
        """
        Create an audio data object
        """
        return cls.objects.create(
            home=home,
            hardware_device_mac_address=hardware_device_mac_address,
            uid=uid,
            sequence_index=sequence_index,
            audio_file=audio_file,
            start_time=start_time,
            end_time=end_time,
            track_id=track_id,
        )

    def __str__(self):
        return f"{self.uid} - {self.audio_file}"

    def url(self):
        """
        get the file, and create media url
        Returns:

        """
        return f"/hardware/client_audio/{self.id}"

    class Meta:
        verbose_name = "Data Audio"
        verbose_name_plural = "Data Audios"


class DataVideo(models.Model):
    """
    Link to home and hardware device, and the video data will be stored in the database
    It will be created by the endpoint from client side when video data is acquired
    Same as the audio data, the video data will be stored in the database
    It will not be directly connected to the audio data
    Audio data and video data will be connected by the time range softly
    """

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
    start_time = models.DateTimeField(help_text="The start time of the video")
    end_time = models.DateTimeField(help_text="The end time of the video")

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the video"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the video"
    )

    def __str__(self):
        return f"{self.uid} - {self.video_file}"

    class Meta:
        verbose_name = "Data Video"
        verbose_name_plural = "Data Videos"


class DataText(models.Model):
    """
    The text data will be stored in the database
    It will be created after speech2text is done
    """

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

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Data Text"
        verbose_name_plural = "Data Texts"


class ResText(models.Model):
    text = models.TextField(help_text="The text of the audio")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the llm response"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the llm response"
    )

    def __str__(self):
        if len(self.text) > 50:
            return f"{self.text[:50]}..."
        return self.text

    class Meta:
        verbose_name = "Res Text"
        verbose_name_plural = "Res Texts"


class ResSpeech(models.Model):
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

    def __str__(self):
        file_name = self.text2speech_file.split("/")[-1]
        return f"{file_name}|Played: {self.played}"

    def url(self):
        return f"/hardware/ai_audio/{self.id}"

    class Meta:
        verbose_name = "Res Speech"
        verbose_name_plural = "Res Speeches"


class DataMultiModalConversation(models.Model):
    """
    It will be created when a audio is created
    Then video will be added when emotion detection is triggered, or other task require video
    Text will be added when speech2text is done
    ResText will be added when the text is processed by the language model
    ResSpeech will be added when the text is processed by the text2speech
    """

    audio = models.OneToOneField(
        DataAudio,
        on_delete=models.SET_NULL,
        related_name="multi_modal_conversation",
        null=True,
        blank=True,
    )
    # video should be an array field
    video = models.ManyToManyField(
        DataVideo, related_name="multi_modal_conversation", blank=True
    )
    text = models.OneToOneField(
        DataText,
        on_delete=models.SET_NULL,
        related_name="multi_modal_conversation",
        null=True,
        blank=True,
    )

    res_text = models.OneToOneField(
        ResText,
        on_delete=models.SET_NULL,
        related_name="multi_modal_conversation",
        null=True,
        blank=True,
    )
    res_speech = models.OneToOneField(
        ResSpeech,
        on_delete=models.SET_NULL,
        related_name="multi_modal_conversation",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The created time of the multi-modal conversation"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The updated time of the multi-modal conversation"
    )

    track_id = models.CharField(
        max_length=100,
        help_text="The track id of the multimodal conversation",
        null=True,
        blank=True,
    )
    annotations = models.JSONField(
        help_text="The annotations of the emotion detection",
        null=True,
        blank=True,
        default=dict,
    )

    def __str__(self):
        return f"{self.id}"

    def video_url(self):
        if len(self.video.all()) == 0:
            return "No Video"
        return f"/hardware/client_video/{self.id}"

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"


class ContextEmotionDetection(models.Model):
    multi_modal_conversation = models.ForeignKey(
        DataMultiModalConversation,
        on_delete=models.CASCADE,
        related_name="emotion_detection",
        null=True,
        blank=True,
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

    annotations = models.JSONField(
        help_text="The annotations of the emotion detection",
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        verbose_name = "Context Emotion"
        verbose_name_plural = "Context Emotions"
