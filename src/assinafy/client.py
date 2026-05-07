from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx

from .errors import ValidationError
from .resources.assignments import AssignmentResource
from .resources.authentication import AuthenticationResource
from .resources.documents import DocumentResource
from .resources.fields import FieldResource
from .resources.signer_documents import SignerDocumentResource
from .resources.signers import SignerResource
from .resources.templates import TemplateResource
from .resources.webhooks import WebhookResource
from .support.webhook_verifier import WebhookVerifier
from .types import Logger
from .utils import create_noop_logger

_DEFAULT_BASE_URL = "https://api.assinafy.com.br/v1"
_USER_AGENT = "assinafy-python-sdk"


class AssinafyClient:
    def __init__(
        self,
        api_key: str | None = None,
        token: str | None = None,
        account_id: str | None = None,
        base_url: str | None = None,
        webhook_secret: str | None = None,
        timeout: float = 30.0,
        logger: Logger | None = None,
    ) -> None:
        self._logger: Logger = logger or create_noop_logger()

        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": _USER_AGENT,
        }
        if api_key:
            headers["X-Api-Key"] = api_key
        elif token:
            headers["Authorization"] = f"Bearer {token}"

        self._http = httpx.Client(
            base_url=(base_url or _DEFAULT_BASE_URL).rstrip("/") + "/",
            timeout=timeout,
            headers=headers,
        )

        self.authentication = AuthenticationResource(self._http, None, self._logger)
        self.documents = DocumentResource(self._http, account_id, self._logger)
        self.signers = SignerResource(self._http, account_id, self._logger)
        self.signer_documents = SignerDocumentResource(self._http, account_id, self._logger)
        self.assignments = AssignmentResource(self._http, account_id, self._logger)
        self.webhooks = WebhookResource(self._http, account_id, self._logger)
        self.templates = TemplateResource(self._http, account_id, self._logger)
        self.fields = FieldResource(self._http, account_id, self._logger)
        self.webhook_verifier = WebhookVerifier(webhook_secret)

    def upload_and_request_signatures(
        self,
        source: dict[str, Any],
        signers: list[dict[str, Any]],
        message: str | None = None,
        wait_for_ready: bool = True,
        expires_at: str | None = None,
        copy_receivers: list[str] | None = None,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        if not signers:
            raise ValidationError("At least one signer is required")

        self._logger.info(
            "Starting upload + signature workflow", {"signer_count": len(signers)}
        )

        document = self.documents.upload(
            source, {"account_id": account_id} if account_id else None
        )
        if wait_for_ready:
            self.documents.wait_until_ready(document["id"])

        signer_ids = [
            self.signers.create(signer, account_id)["id"] for signer in signers
        ]

        assignment_payload: dict[str, Any] = {"method": "virtual", "signers": signer_ids}
        if message is not None:
            assignment_payload["message"] = message
        if expires_at is not None:
            assignment_payload["expires_at"] = expires_at
        if copy_receivers is not None:
            assignment_payload["copy_receivers"] = copy_receivers

        assignment = self.assignments.create(document["id"], assignment_payload)
        self._logger.info(
            "Upload + signature workflow completed", {"document_id": document["id"]}
        )
        return {"document": document, "assignment": assignment, "signer_ids": signer_ids}

    def get_http_client(self) -> httpx.Client:
        return self._http

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> AssinafyClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
