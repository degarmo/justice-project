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
        fields = ['display_name', 'city', 'state', 'message', 'is_anonymous', 'show_location']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your message...'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_location': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
