"""Константы"""

from django.utils.translation import gettext_lazy as _

ERROR_MESSAGES_MAPPING = {
    "email_already_in_use": _(
        "Пользователь с таким email уже зарегистрирован. Попробуйте войти."
    ),
    "invalid_email_format": _(
        "Пожалуйста, введите корректный адрес электронной почты."
    ),
    "forbidden_email_domain": _(
        "Регистрация разрешена только для российских доменов (.ru, .рф, .su)."
    ),
    "user_was_not_created": _(
        "Сервис временно недоступен. Мы уже решаем проблему, попробуйте позже."
    ),
}
