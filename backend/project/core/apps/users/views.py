from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
import logging

from .forms import UserRegistrationForm
from .consts import ERROR_MESSAGES_MAPPING

logger = logging.getLogger(__name__)

class RegisterView(View):
    """Вьюха для регистрации новых пользователей"""
    def get(self, request):
        return render(request, 'register.html', {'form': UserRegistrationForm})