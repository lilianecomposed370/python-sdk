from __future__ import annotations

from typing import Any


class MockResponse:
    def __init__(
        self,
        json_data: Any = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        content: bytes = b"",
    ) -> None:
        self._json_data = json_data if json_data is not None else {}
        self.status_code = status_code
        self.headers = headers or {}
        self.content = content

    def json(self) -> Any:
        return self._json_data

    def raise_for_status(self) -> None:
        pass


def make_response(
    json_data: Any = None,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> MockResponse:
    return MockResponse(json_data=json_data, status_code=status_code, headers=headers)


def make_envelope(data: Any, status: int = 200) -> dict[str, Any]:
    return {"status": status, "data": data}
