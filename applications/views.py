import calendar
from datetime import timedelta

from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.formats import date_format
from django.utils import timezone

from .forms import CompanyContactForm, CompanyCreateForm, CompanyForm, JobApplicationForm
from .models import Company, CompanyContact, JobApplication


def application_list(request):
    applications = JobApplication.objects.all()
    sort = request.GET.get("sort", "recent")
    month = request.GET.get("month", "")
    year = request.GET.get("year", "")

    if sort not in {"recent", "oldest"}:
        sort = "recent"
    applications = applications.order_by("date_applied", "id") if sort == "oldest" else applications.order_by("-date_applied", "-id")

    try:
        month_number = int(month)
        if 1 <= month_number <= 12:
            applications = applications.filter(date_applied__month=month_number)
        else:
            month = ""
    except (TypeError, ValueError):
        month = ""

    try:
        year_number = int(year)
        if 1 <= year_number <= 9999:
            applications = applications.filter(date_applied__year=year_number)
        else:
            year = ""
    except (TypeError, ValueError):
        year = ""

    months = list(
        JobApplication.objects.order_by()
        .values_list("date_applied__month", flat=True)
        .distinct()
        .order_by("date_applied__month")
    )
    month_choices = [
        (value, calendar.month_name[value], str(value) == month)
        for value in months
    ]
    years = list(
        JobApplication.objects.order_by("-date_applied__year")
        .values_list("date_applied__year", flat=True)
        .distinct()
    )
    year_choices = [(value, str(value) == year) for value in years]

    counts = JobApplication.objects.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status__in=[
            JobApplication.Status.APPLIED,
            JobApplication.Status.TEST,
            JobApplication.Status.INTERVIEW,
        ])),
        rejected=Count("id", filter=Q(status=JobApplication.Status.REJECTED)),
    )
    return render(
        request,
        "applications/application_list.html",
        {
            "applications": applications,
            "is_recent": sort == "recent",
            "is_oldest": sort == "oldest",
            "month_choices": month_choices,
            "year_choices": year_choices,
            "counts": counts,
        },
    )


def application_create(request):
    if request.method == "POST":
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("application_list")
    else:
        form = JobApplicationForm()
    return render(request, "applications/application_form.html", {"form": form, "page_title": "Add application"})


def application_update(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method == "POST":
        form = JobApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect("application_list")
    else:
        form = JobApplicationForm(instance=application)
    return render(request, "applications/application_form.html", {"form": form, "page_title": "Edit application"})


def application_delete(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method == "POST":
        application.delete()
        return redirect("application_list")
    return render(request, "applications/application_confirm_delete.html", {"application": application})


def company_list(request):
    companies = Company.objects.annotate(contact_count=Count("contacts", distinct=True))
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    size = request.GET.get("size", "")
    sort = request.GET.get("sort", "name")

    if search:
        companies = companies.filter(
            Q(name__icontains=search)
            | Q(category__icontains=search)
            | Q(description__icontains=search)
            | Q(location__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
            | Q(contact_info__icontains=search)
            | Q(contacts__name__icontains=search)
            | Q(contacts__role__icontains=search)
            | Q(contacts__contact_info__icontains=search)
        ).distinct()
    if status in Company.OutreachStatus.values:
        companies = companies.filter(status=status)
    else:
        status = ""
    if size in Company.Size.values:
        companies = companies.filter(size=size)
    else:
        size = ""

    if sort == "follow_up":
        companies = companies.order_by(F("follow_up_on").asc(nulls_last=True), "name")
    elif sort == "recent":
        companies = companies.order_by("-created_at", "-id")
    else:
        sort = "name"
        companies = companies.order_by("name", "id")

    today = timezone.localdate()
    summary = Company.objects.aggregate(
        total=Count("id"),
        not_contacted=Count(
            "id", filter=Q(status=Company.OutreachStatus.NOT_CONTACTED)
        ),
        contacted=Count("id", filter=Q(status=Company.OutreachStatus.CONTACTED)),
    )
    summary["contacts"] = CompanyContact.objects.count()
    summary["followups_due"] = Company.objects.filter(follow_up_on__lte=today).count()
    summary["followups_due"] += CompanyContact.objects.filter(follow_up_on__lte=today).count()

    return render(
        request,
        "companies/company_list.html",
        {
            "companies": companies,
            "summary": summary,
            "search": search,
            "selected_status": status,
            "selected_size": size,
            "selected_sort": sort,
            "status_choices": [
                (value, label, value == status)
                for value, label in Company.OutreachStatus.choices
            ],
            "size_choices": [
                (value, label, value == size)
                for value, label in Company.Size.choices
            ],
            "sort_choices": [
                ("name", "Company name", sort == "name"),
                ("recent", "Recently added", sort == "recent"),
                ("follow_up", "Next follow-up", sort == "follow_up"),
            ],
            "today": today,
        },
    )


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    contacts = company.contacts.all()
    today = timezone.localdate()
    company.follow_up_display, company.follow_up_class = _follow_up_presentation(
        company.follow_up_on, today
    )
    for contact in contacts:
        contact.follow_up_display, contact.follow_up_class = _follow_up_presentation(
            contact.follow_up_on, today
        )
    return render(
        request,
        "companies/company_detail.html",
        {
            "company": company,
            "contacts": contacts,
        },
    )


def _follow_up_presentation(follow_up_on, today):
    if not follow_up_on:
        return "Not set", ""
    overdue_class = "follow-up-overdue" if follow_up_on < today else ""
    return date_format(follow_up_on, "M j, Y"), overdue_class


def company_create(request):
    if request.method == "POST":
        form = CompanyCreateForm(request.POST)
        if form.is_valid():
            company = form.save()
            return redirect("company_detail", pk=company.pk)
    else:
        form = CompanyCreateForm()
    return render(
        request,
        "companies/company_form.html",
        {"form": form, "page_title": "Add company", "submit_label": "Save company"},
    )


def company_update(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect("company_detail", pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    return render(
        request,
        "companies/company_form.html",
        {"form": form, "page_title": "Edit company", "submit_label": "Save changes"},
    )


def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "POST":
        company.delete()
        return redirect("company_list")
    return render(
        request,
        "companies/outreach_confirm_delete.html",
        {
            "item_name": company.name,
            "item_type": "company",
            "warning": "Deleting this company will also delete its saved contacts.",
            "cancel_url": "company_detail",
            "cancel_pk": company.pk,
        },
    )


def contact_create(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    if request.method == "POST":
        form = CompanyContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.company = company
            contact.save()
            return redirect("company_detail", pk=company.pk)
    else:
        form = CompanyContactForm()
    return render(
        request,
        "companies/contact_form.html",
        {
            "form": form,
            "company": company,
            "page_title": "Add contact",
            "submit_label": "Save contact",
        },
    )


def contact_update(request, pk):
    contact = get_object_or_404(CompanyContact, pk=pk)
    if request.method == "POST":
        form = CompanyContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect("company_detail", pk=contact.company_id)
    else:
        form = CompanyContactForm(instance=contact)
    return render(
        request,
        "companies/contact_form.html",
        {
            "form": form,
            "company": contact.company,
            "page_title": "Edit contact",
            "submit_label": "Save changes",
        },
    )


def contact_delete(request, pk):
    contact = get_object_or_404(CompanyContact, pk=pk)
    company_pk = contact.company_id
    if request.method == "POST":
        contact.delete()
        return redirect("company_detail", pk=company_pk)
    return render(
        request,
        "companies/outreach_confirm_delete.html",
        {
            "item_name": contact.name,
            "item_type": "contact",
            "warning": "This only deletes the saved contact, not the company.",
            "cancel_url": "company_detail",
            "cancel_pk": company_pk,
        },
    )