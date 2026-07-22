from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
import logging

from .application.dto import RegisterUserRequest
from .domain.exceptions import UserEmailAlreadyInUseError, CannotCreateUserError, ForbiddenEmailDomainError
from .forms import UserRegistrationForm
from .consts import ERROR_MESSAGES_MAPPING
from .application.use_cases import CreateUserUseCase
from .infrastructure.repositories import DjangoUserRepository
from .domain.constants import ALLOWED_DOMAINS


logger = logging.getLogger(__name__)

class RegisterView(View):
    def __init__(self):
        self.use_case = CreateUserUseCase(
            user_repository=DjangoUserRepository()
        )
    """Вьюха для регистрации новых пользователей"""
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form})
    
    def post(self,request):
        form = UserRegistrationForm(request.POST)

        if not form.is_valid():
            print(f"Ошибки формы: {form.errors}")
            print(f"Ошибки полей: {form.errors.as_data()}")
            print(f"Невалидные данные: {request.POST}")
            return render(request, 'register.html', {'form': form})
        
        dto = RegisterUserRequest(
            email=form.cleaned_data['email'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password'],
        )

        try:
            self.use_case.execute(dto)
        except UserEmailAlreadyInUseError:
            form.add_error('email', 'Пользователь с таким email уже существует')
            return render(request, 'register.html',{
                'form': form
            })
        except CannotCreateUserError:
            return render(request, 'register.html',{
                'form': form,
                'error': 'Ошибка сервера'
            })
        except ForbiddenEmailDomainError:
            form.add_error('email', f'Разрёшенные домены: {','.join(ALLOWED_DOMAINS)}')
            return render(request, 'register.html',{
                'form': form
            })
        else:
            return redirect(reverse('users:login'))


class LoginView(View):
    """Вьюха для авторизации"""
    def get(self, request):
        return render(request, 'login.html')