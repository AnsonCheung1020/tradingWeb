from django.urls import path
from . import views

app_name = "wedges"

urlpatterns = [
    path('', views.wedge_screener_view, name='wedges'),
    path('terminate/', views.terminate_screener, name='terminate_screener'),
]
