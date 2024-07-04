from django import forms


class MultiModalAnnotationForm(forms.ModelForm):
    annotation_speech2text = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 1})
    )
    annotation_speech2text_score = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"min": -10, "max": 10}),
        required=False,
    )
    annotation_text_generation = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 1})
    )

    annotation_text_generation_score = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"min": -10, "max": 10}),
        required=False,
    )

    annotation_text2speech_score = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"min": -10, "max": 10}),
        required=False,
    )

    annotation_overall_score = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"min": -10, "max": 10}),
        required=False,
    )

    annotation_overall_comment = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 1})
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


class MultiModalFKEmotionDetectionAnnotationForm(forms.ModelForm):

    annotation_overall = forms.IntegerField(initial=0)
    annotation_overall.widget.attrs.update({"min": -10, "max": 10})

    annotation_text_modality = forms.IntegerField(initial=0)
    annotation_text_modality.widget.attrs.update({"min": -10, "max": 10})

    annotation_audio_modality = forms.IntegerField(initial=0)
    annotation_audio_modality.widget.attrs.update({"min": -10, "max": 10})

    annotation_video_modality = forms.IntegerField(initial=0)
    annotation_video_modality.widget.attrs.update({"min": -10, "max": 10})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.annotations:
            current_user_annotation = self.instance.annotations.get(
                str(self.current_user.id), {}
            )
            for key, value in current_user_annotation.items():
                if key in self.fields:
                    self.fields[key].initial = value
