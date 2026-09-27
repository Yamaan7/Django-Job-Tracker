from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import JobApplication


class ApplicationListTests(TestCase):
    def setUp(self):
        JobApplication.objects.create(
            post_name="Engineer",
            organization="Northwind",
            date_applied=date(2026, 9, 10),
            status=JobApplication.Status.APPLIED,
        )
        JobApplication.objects.create(
            post_name="Analyst",
            organization="Contoso",
            date_applied=date(2026, 9, 12),
            status=JobApplication.Status.REJECTED,
        )
        JobApplication.objects.create(
            post_name="Designer",
            organization="Northwind Labs",
            date_applied=date(2026, 9, 15),
            status=JobApplication.Status.INTERVIEW,
        )

    def test_dashboard_counts_all_applications(self):
        response = self.client.get(reverse("application_list"))

        self.assertEqual(response.context["counts"], {"total": 3, "pending": 2, "rejected": 1})

    def test_sorts_oldest_first(self):
        response = self.client.get(
            reverse("application_list"),
            {"sort": "oldest"},
        )

        self.assertEqual(
            [item.post_name for item in response.context["applications"]],
            ["Engineer", "Analyst", "Designer"],
        )
        self.assertContains(response, 'class="sort-option active">Oldest</button>')

    def test_month_choices_only_include_months_with_applications(self):
        response = self.client.get(reverse("application_list"))

        self.assertEqual(response.context["month_choices"], [(9, "September", False)])

    def test_filters_by_month_and_year(self):
        JobApplication.objects.create(
            post_name="Developer",
            organization="Fabrikam",
            date_applied=date(2025, 9, 15),
            status=JobApplication.Status.APPLIED,
        )
        response = self.client.get(reverse("application_list"), {"month": "9", "year": "2026"})

        self.assertEqual(
            [item.post_name for item in response.context["applications"]],
            ["Designer", "Analyst", "Engineer"],
        )