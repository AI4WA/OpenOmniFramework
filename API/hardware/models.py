from django.db import models


# Create your models here.

class AudioData(models.Model):
    uid = models.CharField(max_length=100)
    sequence_index = models.IntegerField(help_text="The sequence index of the audio")
    text = models.TextField(help_text="The text of the audio")
    audio_file = models.CharField(max_length=100, help_text="The audio file")
    start_time = models.DateTimeField(help_text="The start time of the audio")
    end_time = models.DateTimeField(help_text="The end time of the audio")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The created time of the audio")
    updated_at = models.DateTimeField(auto_now=True, help_text="The updated time of the audio")

    class Meta:
        db_table = 'audio_data'
        unique_together = ('uid', 'sequence_index')

    def __str__(self):
        return f"{self.uid} {self.sequence_index} {self.text}"
