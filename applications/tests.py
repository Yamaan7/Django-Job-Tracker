from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .forms import CompanyCreateForm, CompanyForm
from .models import Company, CompanyContact, JobApplication


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


class CompanyOutreachTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Northwind",
            contact_info="hello@northwind.example",
            website_url="https://northwind.example",
            size=Company.Size.MEDIUM,
        )

    def test_company_list_shows_summary_and_filters_by_contact(self):
        contact = CompanyContact.objects.create(
            company=self.company,
            name="Morgan Lee",
            role="Engineering Manager",
            contact_info="morgan@northwind.example",
        )

        response = self.client.get(reverse("company_list"), {"q": "Morgan"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary"]["total"], 1)
        self.assertEqual(response.context["summary"]["contacts"], 1)
        self.assertEqual(list(response.context["companies"]), [self.company])
        self.assertEqual(contact.company_id, self.company.pk)

    def test_company_list_filters_by_outreach_status_and_size(self):
        contacted_company = Company.objects.create(
            name="Contoso",
            status=Company.OutreachStatus.CONTACTED,
            size=Company.Size.SMALL,
        )

        response = self.client.get(
            reverse("company_list"),
            {"status": Company.OutreachStatus.CONTACTED, "size": Company.Size.SMALL},
        )

        self.assertEqual(list(response.context["companies"]), [contacted_company])

    def test_company_form_orders_fields_and_uses_text_category(self):
        self.assertEqual(
            list(CompanyForm().fields),
            [
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
            ],
        )
        self.assertEqual(CompanyForm().fields["category"].widget.input_type, "text")

    def test_company_create_form_only_contains_company_details(self):
        self.assertEqual(
            list(CompanyCreateForm().fields),
            ["name", "size", "category", "description", "location", "phone", "email", "website_url", "linkedin_url"],
        )

    def test_add_company_page_hides_outreach_fields(self):
        response = self.client.get(reverse("company_create"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Outreach status")
        self.assertNotContains(response, "Last contacted")
        self.assertNotContains(response, "Follow-up date")

    def test_company_edit_form_keeps_outreach_fields(self):
        self.assertIn("status", CompanyForm().fields)
        self.assertIn("last_contacted_on", CompanyForm().fields)
        self.assertIn("follow_up_on", CompanyForm().fields)

    def test_company_table_shows_phone_and_email_together(self):
        self.company.phone = "+1 555 0100"
        self.company.email = "hello@northwind.example"
        self.company.category = "Healthcare"
        self.company.description = (
            "Healthcare technology company building tools for clinical teams around the world"
        )
        self.company.location = "Seattle"
        self.company.linkedin_url = "https://www.linkedin.com/company/northwind"
        self.company.save()

        response = self.client.get(reverse("company_list"))

        self.assertContains(response, "+1 555 0100")
        self.assertContains(response, "hello@northwind.example")
        self.assertContains(response, "Healthcare")
        self.assertNotContains(response, "<th>Description</th>")
        self.assertNotContains(response, "Healthcare technology company building tools")
        self.assertContains(response, "Seattle")
        self.assertContains(response, 'data-label="No.">1')
        self.assertContains(response, "data-copy-text=\"+1 555 0100\"")
        self.assertContains(response, "data-copy-text=\"hello@northwind.example\"")
        self.assertContains(response, "data-copy-row")
        self.assertContains(response, "https://www.linkedin.com/company/northwind")

    def test_company_without_phone_or_email_shows_centered_dash(self):
        Company.objects.create(name="No Contact Details")

        response = self.client.get(reverse("company_list"))

        self.assertContains(
            response,
            '<div class="company-contact-empty">-</div>',
            html=True,
        )
        self.assertNotContains(response, "company.contact_info")

    def test_company_marked_contacted_gets_seven_day_follow_up(self):
        contacted_on = date(2026, 9, 20)

        response = self.client.post(
            reverse("company_update", args=[self.company.pk]),
            {
                "name": self.company.name,
                "email": "team@fabrikam.example",
                "phone": "555-0101",
                "category": "Technology",
                "location": "Seattle",
                "website_url": self.company.website_url,
                "size": Company.Size.LARGE,
                "status": Company.OutreachStatus.CONTACTED,
                "last_contacted_on": contacted_on.isoformat(),
                "follow_up_on": "",
            },
        )

        company = Company.objects.get(pk=self.company.pk)
        self.assertRedirects(response, reverse("company_detail", args=[company.pk]))
        self.assertEqual(company.follow_up_on, contacted_on + timedelta(days=7))

    def test_contact_is_created_under_its_company_with_follow_up(self):
        contacted_on = date(2026, 9, 21)

        response = self.client.post(
            reverse("contact_create", args=[self.company.pk]),
            {
                "name": "Taylor Chen",
                "role": "Recruiter",
                "contact_info": "taylor@northwind.example",
                "linkedin_url": "https://www.linkedin.com/in/taylor-chen",
                "status": Company.OutreachStatus.CONTACTED,
                "last_contacted_on": contacted_on.isoformat(),
                "follow_up_on": "",
            },
        )

        contact = CompanyContact.objects.get(name="Taylor Chen")
        self.assertRedirects(response, reverse("company_detail", args=[self.company.pk]))
        self.assertEqual(contact.company, self.company)
        self.assertEqual(contact.follow_up_on, contacted_on + timedelta(days=7))

    def test_company_detail_shows_nested_contacts(self):
        CompanyContact.objects.create(company=self.company, name="Morgan Lee", role="Manager")

        response = self.client.get(reverse("company_detail", args=[self.company.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Morgan Lee")
        self.assertContains(response, "People to contact")

    def test_deleting_company_also_deletes_contacts(self):
        contact = CompanyContact.objects.create(company=self.company, name="Morgan Lee")

        response = self.client.post(reverse("company_delete", args=[self.company.pk]))

        self.assertRedirects(response, reverse("company_list"))
        self.assertFalse(Company.objects.filter(pk=self.company.pk).exists())
        self.assertFalse(CompanyContact.objects.filter(pk=contact.pk).exists())