from __future__ import annotations

from typing import Any

import httpx

from .errors import ApiError, AssinafyError, NetworkError
from .types import Logger

QUERY_PARAM_ALIASES = {
    "per_page": "per-page",
    "signer_access_code": "signer-access-code",
}


def handle_assinafy_response(response: Any) -> Any:
    if isinstance(response, dict) and "status" in response and "data" in response:
        status = response["status"]
        if isinstance(status, int) and 200 <= status < 300:
            return response["data"]
        raise ApiError.from_response(status, response)
    return response


def to_sdk_error(error: Exception, fallback_message: str) -> AssinafyError:
    if isinstance(error, AssinafyError):
        return error

    if isinstance(error, httpx.HTTPStatusError):
        try:
            data: Any = error.response.json()
        except ValueError:
            data = None
        return ApiError.from_response(error.response.status_code, data)

    if isinstance(error, httpx.RequestError):
        return NetworkError(f"{fallback_message}: {error}")

    return AssinafyError(f"{fallback_message}: {error}")


class _NoopLogger:
    def debug(self, message: str, context: dict[str, Any] | None = None) -> None: ...
    def info(self, message: str, context: dict[str, Any] | None = None) -> None: ...
    def warning(self, message: str, context: dict[str, Any] | None = None) -> None: ...
    def error(self, message: str, context: dict[str, Any] | None = None) -> None: ...


_NOOP_LOGGER: Logger = _NoopLogger()


def create_noop_logger() -> Logger:
    return _NOOP_LOGGER


def clean_params(
    params: dict[str, Any],
    aliases: dict[str, str] | None = None,
) -> dict[str, Any]:
    aliases = aliases or {}
    return {aliases.get(k, k): v for k, v in params.items() if v is not None}
