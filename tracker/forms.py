from django import forms
from .models import TipSubmission, MessageOfLove


class TipSubmissionForm(forms.ModelForm):
    class Meta:
        model = TipSubmission
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

class MessageOfLoveForm(forms.ModelForm):
    class Meta:
        model = MessageOfLove
        fields = ['display_name', 'city', 'state', 'message', 'is_anonymous', 'show_location', 'shared_social']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
