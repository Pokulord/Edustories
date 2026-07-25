"""Исключения на уровне сценариев (use-cases)"""

class ApplicationError(Exception):
    """Базовая ошибка уровня сценария (use-case)."""

    error_slug: str = "application_error"
    message: str = "Произошла ошибка на уровне сценария"

    def __init__(self, message: str | None = None, metadata: dict | None = None):
        if message:
            self.message = message
        self.metadata = metadata if metadata else {}
        super().__init__(self.message)

class AuthenticationFailed(ApplicationError):
    """Неверные учетные данные"""

    error_slug: str = "authentication_failed"
    message: str = "Неверный email или пароль"

    def __init__(self, email: str | None = None):
        super().__init__(
            metadata={"email": email}
        )