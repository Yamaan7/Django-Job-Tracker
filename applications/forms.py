from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Company, CompanyContact, JobApplication


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["post_name", "organization", "fee_paid", "date_applied", "status"]
        widgets = {
            "date_applied": forms.DateInput(attrs={"type": "date"}),
        }


class OutreachFollowUpMixin:
    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("status") == Company.OutreachStatus.CONTACTED
            and not cleaned_data.get("follow_up_on")
        ):
            last_contacted_on = cleaned_data.get("last_contacted_on") or timezone.localdate()
            cleaned_data["last_contacted_on"] = last_contacted_on
            cleaned_data["follow_up_on"] = last_contacted_on + timedelta(days=7)
        return cleaned_data


class CompanyForm(OutreachFollowUpMixin, forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name",
            "size",
            "category",
            "description",
            "location",
            "phone",
            "email",
            "website_url",
            "linkedin_url",
            "status",
            "last_contacted_on",
            "follow_up_on",
        ]
        labels = {
            "name": "Company name",
            "size": "Company size",
            "category": "Category",
            "description": "Company description",
            "location": "Location",
            "phone": "Phone",
            "email": "Email",
            "website_url": "Website URL",
            "linkedin_url": "LinkedIn URL",
            "status": "Outreach status",
            "last_contacted_on": "Last contacted",
            "follow_up_on": "Follow-up date",
        }
        help_texts = {
            "follow_up_on": "If marked contacted and left blank, this defaults to 7 days after the contact date.",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "last_contacted_on": forms.DateInput(attrs={"type": "date"}),
            "follow_up_on": forms.DateInput(attrs={"type": "date"}),
        }


class CompanyCreateForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        fields = [
            "name",
            "size",
            "category",
            "description",
            "location",
            "phone",
            "email",
            "website_url",
            "linkedin_url",
        ]


class CompanyContactForm(OutreachFollowUpMixin, forms.ModelForm):
    class Meta:
        model = CompanyContact
        fields = [
            "name",
            "role",
            "contact_info",
            "linkedin_url",
            "status",
            "last_contacted_on",
            "follow_up_on",
        ]
        labels = {
            "name": "Employee name",
            "role": "Role",
            "contact_info": "Email or contact info",
            "linkedin_url": "LinkedIn profile URL",
            "status": "Outreach status",
            "last_contacted_on": "Last contacted",
            "follow_up_on": "Follow-up date",
        }
        help_texts = {
            "follow_up_on": "If marked contacted and left blank, this defaults to 7 days after the contact date.",
        }
        widgets = {
            "last_contacted_on": forms.DateInput(attrs={"type": "date"}),
            "follow_up_on": forms.DateInput(attrs={"type": "date"}),
        }