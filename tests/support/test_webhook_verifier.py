from __future__ import annotations

import hashlib
import hmac
import json

from assinafy.support.webhook_verifier import WebhookVerifier


def _generate_signature(secret: str, payload: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class TestWebhookVerifier:
    def setup_method(self) -> None:
        self.secret = "super-secret"
        self.payload = json.dumps(
            {"event": "document_ready", "data": {"document_id": "doc-1"}}
        )
        self.signature = _generate_signature(self.secret, self.payload)

    def test_verify_returns_true_for_matching_hmac_sha256_signature(self) -> None:
        verifier = WebhookVerifier(self.secret)
        assert verifier.verify(self.payload, self.signature) is True

    def test_verify_returns_false_for_mismatched_signature(self) -> None:
        verifier = WebhookVerifier(self.secret)
        assert verifier.verify(self.payload, "deadbeef") is False

    def test_verify_returns_false_when_no_secret_is_configured(self) -> None:
        verifier = WebhookVerifier(None)
        assert verifier.verify(self.payload, self.signature) is False

    def test_verify_accepts_bytes_payload(self) -> None:
        verifier = WebhookVerifier(self.secret)
        assert verifier.verify(self.payload.encode("utf-8"), self.signature) is True

    def test_verify_returns_false_for_empty_signature(self) -> None:
        verifier = WebhookVerifier(self.secret)
        assert verifier.verify(self.payload, "") is False

    def test_extract_event_parses_json_payloads(self) -> None:
        verifier = WebhookVerifier(self.secret)
        result = verifier.extract_event(self.payload)
        assert result == {"event": "document_ready", "data": {"document_id": "doc-1"}}

    def test_extract_event_parses_bytes_payload(self) -> None:
        verifier = WebhookVerifier(self.secret)
        result = verifier.extract_event(self.payload.encode("utf-8"))
        assert result == {"event": "document_ready", "data": {"document_id": "doc-1"}}

    def test_extract_event_returns_none_on_malformed_payload(self) -> None:
        verifier = WebhookVerifier(self.secret)
        assert verifier.extract_event("{not json") is None

    def test_get_event_type_and_get_event_data_unwrap_envelope(self) -> None:
        verifier = WebhookVerifier(self.secret)
        event = verifier.extract_event(self.payload)
        assert verifier.get_event_type(event) == "document_ready"
        assert verifier.get_event_data(event) == {"document_id": "doc-1"}

    def test_get_event_type_falls_back_to_type_field(self) -> None:
        verifier = WebhookVerifier(self.secret)
        event_type = verifier.get_event_type({"type": "signer_signed_document"})
        assert event_type == "signer_signed_document"

    def test_get_event_type_returns_none_for_none_event(self) -> None:
        verifier = WebhookVerifier(self.secret)
        assert verifier.get_event_type(None) is None

    def test_get_event_data_returns_empty_dict_for_none_event(self) -> None:
        verifier = WebhookVerifier(self.secret)
        assert verifier.get_event_data(None) == {}

    def test_get_event_data_falls_back_to_object_field(self) -> None:
        verifier = WebhookVerifier(self.secret)
        event = {"object": {"id": "doc-1"}}
        assert verifier.get_event_data(event) == {"id": "doc-1"}
