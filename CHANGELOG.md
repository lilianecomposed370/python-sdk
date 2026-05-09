# Changelog

All notable changes to `assinafy` are documented in this file.

## [1.1.0] - 2026-05-07

### Changed

- `signers.create` now follows the documented API exactly: it `POST`s the payload directly without an implicit "find by email then short-circuit" lookup or a 409-recovery refetch.
- `signers.update` now requires at least one documented field (`full_name`, `email`, or `whatsapp_phone_number`).
- `upload_and_request_signatures` now expects `full_name` (matching the API) instead of `name`.
- `BaseResource` is now typed against `httpx.Client` and `Logger`; the no-op logger is exposed via the `Logger` Protocol.

### Added

- `py.typed` marker (PEP 561) so consumers get inline type hints.

### Removed

- `documents.is_fully_signed` and `documents.get_signing_progress` — derive from `documents.get(id)` instead.
- `AssignmentVerificationMethod` and `AssignmentNotificationMethod` aliases (they were just `str`).

## [1.0.0] - 2026-04-10

### Added

- Initial synchronous Python SDK release with `httpx`.
- Core resources for documents, signers, assignments, webhooks, and workspaces.
- `WebhookVerifier` with HMAC-SHA256 verification.
- Pytest test suite.