from django.urls import path
from . import views
app_name = "EMA821"

urlpatterns = [
    path('EMA821/', views.EMA821_view, name = 'EMA821'),
   
    
]
