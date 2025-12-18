from typing import Any


class AppException(Exception):
    """Базовое исключение для всего приложения."""
    def __init__(
            self,
            message: str = "An internal error occurred",
            status_code: int = 500,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Исключение для случаев, когда ресурс не найден (404)."""
    def __init__(self, resource: str, identifier: Any):
        self.resource = resource
        self.identifier = identifier
        message = f"{resource} with identifier {identifier} not found"
        super().__init__(message=message, status_code=404)
