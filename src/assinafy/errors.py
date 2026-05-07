from __future__ import annotations

from typing import Any


class AssinafyError(Exception):
    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.context: dict[str, Any] = context or {}


class ApiError(AssinafyError):
    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: Any = None,
    ) -> None:
        super().__init__(message, {"status_code": status_code, "response_data": response_data})
        self.status_code = status_code
        self.response_data = response_data

    @classmethod
    def from_response(cls, status_code: int, response_data: Any) -> ApiError:
        data = response_data if isinstance(response_data, dict) else {}
        raw_message = data.get("message")
        raw_error = data.get("error")
        if isinstance(raw_message, str) and raw_message:
            message = raw_message
        elif isinstance(raw_error, str) and raw_error:
            message = raw_error
        else:
            message = "API request failed"
        return cls(message, status_code, response_data)


class ValidationError(AssinafyError):
    def __init__(
        self,
        message: str = "Validation failed",
        errors: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, {"errors": errors or {}})
        self.errors: dict[str, Any] = errors or {}


class NetworkError(AssinafyError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
