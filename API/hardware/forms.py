from django import forms


class MultiModalAnnotationForm(forms.ModelForm):
    annotation_speech2text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 1}),
        help_text="Please provide your annotation for the speech-to-text task.",
    )
    annotation_speech2text_score = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"min": 0, "max": 5}),
        required=False,
        help_text="Score for the speech-to-text results, score from 0 to 5.",
    )
    annotation_text_generation = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 1}),
        help_text="Please provide your annotation for the text generation task.",
    )

    annotation_text_generation_score = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"min": 0, "max": 5}),
        required=False,
        help_text="Score for the text generation results, score from 0 to 5.",
    )

    annotation_text2speech_score = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"min": 0, "max": 5}),
        required=False,
        help_text="Score for the text-to-speech results, score from 0 to 5.",
    )

    annotation_overall_score = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"min": 0, "max": 5}),
        required=False,
        help_text="Overall score for this multi-modal task, score from 0 to 5.",
    )

    annotation_overall_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 1}),
        help_text="Please provide your overall annotation for this multi-modal task.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.annotations:
            current_user_annotation = self.instance.annotations.get(
                str(self.current_user.id), {}
            )
            for key, value in current_user_annotation.items():
                if key in self.fields:
                    self.fields[key].initial = value
        if self.instance.multi_turns_annotations:
            current_user_annotation = self.instance.multi_turns_annotations.get(
                str(self.current_user.id), {}
            )
            for key, value in current_user_annotation.items():
                if key in self.fields:
                    self.fields[key].initial = value


class MultiModalFKEmotionDetectionAnnotationForm(forms.ModelForm):

    annotation_overall = forms.IntegerField(
        initial=0,
        help_text="Overall score for this emotion detection task, score from 0 to 5.",
    )
    annotation_overall.widget.attrs.update({"min": 0, "max": 5})

    annotation_text_modality = forms.IntegerField(
        initial=0, help_text="Score for text modality."
    )
    annotation_text_modality.widget.attrs.update({"min": 0, "max": 5})

    annotation_audio_modality = forms.IntegerField(
        initial=0, help_text="Score for audio modality."
    )
    annotation_audio_modality.widget.attrs.update({"min": 0, "max": 5})

    annotation_video_modality = forms.IntegerField(
        initial=0, help_text="Score for video modality."
    )
    annotation_video_modality.widget.attrs.update({"min": 0, "max": 5})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.annotations:
            current_user_annotation = self.instance.annotations.get(
                str(self.current_user.id), {}
            )
            for key, value in current_user_annotation.items():
                if key in self.fields:
                    self.fields[key].initial = value
