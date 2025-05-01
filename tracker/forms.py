from django import forms
from .models import TipSubmission

class TipSubmissionForm(forms.ModelForm):
    class Meta:
        model = TipSubmission
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
