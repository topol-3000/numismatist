from typing import Any

from utils.enums import ErrorCode


class BaseError(Exception):
    def __init__(self, message: str, code: ErrorCode, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self._code: ErrorCode = code
        self._message: str = message
        self._details: dict[str, Any] | None = details

    @property
    def code(self) -> str:
        return self._code.value

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> list[dict[str, Any] | None]:
        return [self._details] if self._details else []


class DatabaseError(BaseError):
    def __init__(self, message: str, code: ErrorCode, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code=code, details=details)
