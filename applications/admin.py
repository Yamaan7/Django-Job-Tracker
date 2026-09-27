from django.contrib import admin

from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("post_name", "organization", "date_applied", "status", "fee_paid")
    list_filter = ("status",)