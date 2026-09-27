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


class Company(models.Model):
    class Size(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        SMALL = "1-10", "1-10 employees"
        GROWING = "11-50", "11-50 employees"
        MEDIUM = "51-200", "51-200 employees"
        LARGE = "201-500", "201-500 employees"
        ENTERPRISE = "501+", "501+ employees"

    class OutreachStatus(models.TextChoices):
        NOT_CONTACTED = "not_contacted", "Not contacted"
        CONTACTED = "contacted", "Contacted"

    name = models.CharField(max_length=200)
    size = models.CharField(max_length=20, choices=Size.choices, default=Size.UNKNOWN)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    contact_info = models.CharField(max_length=300, blank=True)
    website_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=OutreachStatus.choices,
        default=OutreachStatus.NOT_CONTACTED,
    )
    last_contacted_on = models.DateField(null=True, blank=True)
    follow_up_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "id"]
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class CompanyContact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True)
    contact_info = models.CharField(max_length=300, blank=True)
    linkedin_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Company.OutreachStatus.choices,
        default=Company.OutreachStatus.NOT_CONTACTED,
    )
    last_contacted_on = models.DateField(null=True, blank=True)
    follow_up_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return f"{self.name} ({self.company.name})"