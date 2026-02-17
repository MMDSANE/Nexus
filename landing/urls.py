# landing/urls.py
from django.urls import path
from .views import *

app_name = 'landing'

urlpatterns = [
    path('', landing_view, name='landing_view'),
]
