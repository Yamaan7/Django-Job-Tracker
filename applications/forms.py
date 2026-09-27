from django import forms

from .models import JobApplication


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["post_name", "organization", "fee_paid", "date_applied", "status"]
        widgets = {
            "date_applied": forms.DateInput(attrs={"type": "date"}),
        }