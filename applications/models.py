from django.db import models


class JobApplication(models.Model):
    class Status(models.TextChoices):
        APPLIED = "Applied", "Applied"
        TEST = "Test", "Test"
        INTERVIEW = "Interview", "Interview"
        REJECTED = "Rejected", "Rejected"
        SELECTED = "Selected", "Selected"

    post_name = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    fee_paid = models.IntegerField(default=0)
    date_applied = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)

    class Meta:
        ordering = ["-date_applied", "-id"]

    def __str__(self):
        return f"{self.post_name} at {self.organization}"