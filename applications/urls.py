from django.urls import path

from . import views


urlpatterns = [
    path("", views.application_list, name="application_list"),
    path("applications/add/", views.application_create, name="application_create"),
    path("applications/<int:pk>/edit/", views.application_update, name="application_update"),
    path("applications/<int:pk>/delete/", views.application_delete, name="application_delete"),
    path("companies/", views.company_list, name="company_list"),
    path("companies/add/", views.company_create, name="company_create"),
    path("companies/<int:pk>/edit/", views.company_update, name="company_update"),
    path("companies/<int:pk>/delete/", views.company_delete, name="company_delete"),
    path("companies/<int:company_pk>/contacts/add/", views.contact_create, name="contact_create"),
    path("companies/contacts/<int:pk>/edit/", views.contact_update, name="contact_update"),
    path("companies/contacts/<int:pk>/delete/", views.contact_delete, name="contact_delete"),
    path("companies/<int:pk>/", views.company_detail, name="company_detail"),
]