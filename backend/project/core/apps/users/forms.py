from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    """
    Форма для создания нового пользователя.
    Используется для регистрации новых студентов.
    """
    
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    
    first_name = forms.CharField(
        label=_("Имя"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )
    
    last_name = forms.CharField(
        label=_("Фамилия"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите вашу фамилию'
        })
    )
    
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        """
        Проверка, что email уникален
        """
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('Пользователь с таким email уже существует')
            )
        return email
    
    def clean_password2(self):
        """
        Проверка совпадения паролей
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _('Пароли не совпадают')
            )
        return password2
    
    def save(self, commit=True):
        """
        Сохранение пользователя с ролью STUDENT
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = CustomUser.Role.STUDENT  # Автоматически назначаем роль STUDENT
        
        if hasattr(user, 'username'):
            user.username = self.cleaned_data['email']
        
        if commit:
            user.save()
        
        return user
