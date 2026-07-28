from django.urls import path
from . import views
app_name="cup_and_h"

urlpatterns=[
    path('cup_and_h/', views.stock_screener_view, name='cup_and_h'),
]