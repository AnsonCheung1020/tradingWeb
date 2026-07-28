from django.urls import path
from . import views

app_name = "quant_lab"

urlpatterns = [
    path("quant_lab/", views.index, name="index"),
    path("quant_lab/<slug:slug>/", views.detail, name="detail"),
    path("quant_lab/<slug:slug>/edit/", views.edit_thesis, name="edit_thesis"),
]
