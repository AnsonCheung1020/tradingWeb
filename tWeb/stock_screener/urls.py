from django.urls import path
from . import views
app_name = "stock_screener"

urlpatterns=[
    path('stock_screener/', views.stock_screener_view, name='stock_screener'),
]