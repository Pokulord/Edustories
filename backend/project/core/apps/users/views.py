from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
import logging

from .application.dto import RegisterUserRequest, LoginUserRequest
from .domain.exceptions import UserEmailAlreadyInUseError, CannotCreateUserError, ForbiddenEmailDomainError, UserIsNotActiveError
from .forms import UserRegistrationForm, LoginForm
from .consts import ERROR_MESSAGES_MAPPING
from .application.use_cases import CreateUserUseCase, LoginUserUseCase
from .infrastructure.repositories import DjangoUserRepository
from .domain.constants import ALLOWED_DOMAINS


class RegisterView(View):
    def __init__(self):
        self.use_case = CreateUserUseCase(
            user_repository=DjangoUserRepository()
        )
    """Вьюха для регистрации новых пользователей"""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:user_profile')
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
    def __init__(self):
        self.use_case = LoginUserUseCase(
            user_repository=DjangoUserRepository()
        )
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:user_profile')
        return render(request, 'login.html')
    def post(self, request):
        form = LoginForm(request.POST)

        if not form.is_valid():
            print(f"Ошибки формы: {form.errors}")
            print(f"Ошибки полей: {form.errors.as_data()}")
            print(f"Невалидные данные: {request.POST}")
            return render(request, 'login.html', {'form': form})
        
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(request, email=email, password=password)

        if user is None:
            # В качестве первого аргумента мы передаём имя поля, к которому относится ошибка
            # Если передать None, то это станет общей ошибкой формы
            form.add_error(None, "Неверное имя пользователя или пароль")
            return render(request, 'login.html', {'form': form})
        
        dto = LoginUserRequest(
            email
        )
        try: 
            self.use_case.execute(dto)
        except UserIsNotActiveError:
            form.add_error(None, "Пользователь неактивен")
            return render(request, 'login.html', {'form': form})
        else:
            login(request, user)
            return redirect(reverse('users:user_profile'))

class ProfileView(LoginRequiredMixin,View):
    """Вьюха для профиля польльзователя"""
    def get(self, request):
        return render(request, 'profile.html')