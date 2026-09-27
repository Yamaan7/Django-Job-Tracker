from django.urls import path

from . import views


urlpatterns = [
    path("", views.application_list, name="application_list"),
    path("applications/add/", views.application_create, name="application_create"),
    path("applications/<int:pk>/edit/", views.application_update, name="application_update"),
    path("applications/<int:pk>/delete/", views.application_delete, name="application_delete"),
]