from django import forms
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(forms.Form):
    """
    Форма для создания нового пользователя
    """

    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@email.com"}
        ),
    )

    first_name = forms.CharField(
        label=_("Имя"),
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Введите ваше имя"}
        ),
    )

    last_name = forms.CharField(
        label=_("Фамилия"),
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Введите вашу фамилию"}
        ),
    )

    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )

    password_confirm = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Повторите пароль"}
        ),
    )

    def clean(self):
        """
        Проверка формы
        """
        cleaned_data = super().clean()
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(_("Пароли не совпадают"))
        return cleaned_data
