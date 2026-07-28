#from django.http import HttpResponse
from django.shortcuts import render  ## streamline the process of rendering templates.

def homepage(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def screeners(request):
    return render (request, 'screeners.html' )


