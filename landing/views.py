import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def landing_view(request):
    context = {}
    return render(request, 'landing/index.html', context)