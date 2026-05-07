from __future__ import annotations

from typing import Any, Literal, Protocol

DocumentStatus = Literal[
    "uploading",
    "uploaded",
    "metadata_processing",
    "metadata_ready",
    "pending_signature",
    "expired",
    "certificating",
    "certificated",
    "rejected_by_signer",
    "rejected_by_user",
    "failed",
]

DocumentArtifactName = Literal["original", "certificated", "certificate-page", "bundle"]

AssignmentMethod = Literal["virtual", "collect"]

WebhookEventType = Literal[
    "document_uploaded",
    "document_metadata_ready",
    "document_prepared",
    "assignment_created",
    "document_ready",
    "signature_requested",
    "signer_created",
    "signer_email_verified",
    "signer_whatsapp_verified",
    "signer_data_confirmed",
    "signer_viewed_document",
    "signer_signed_document",
    "signer_rejected_document",
    "user_rejected_document",
    "document_processing_failed",
    "template_created",
    "template_processed",
    "template_processing_failed",
]

SignerReference = str | dict[str, Any]


class Logger(Protocol):
    def debug(self, message: str, context: dict[str, Any] | None = None) -> None: ...
    def info(self, message: str, context: dict[str, Any] | None = None) -> None: ...
    def warning(self, message: str, context: dict[str, Any] | None = None) -> None: ...
    def error(self, message: str, context: dict[str, Any] | None = None) -> None: ...
