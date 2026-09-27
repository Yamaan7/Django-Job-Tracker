import calendar

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import JobApplicationForm
from .models import JobApplication


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