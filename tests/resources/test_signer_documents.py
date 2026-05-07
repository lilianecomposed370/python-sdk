from __future__ import annotations

from assinafy.resources.signer_documents import SignerDocumentResource
from tests.conftest import MockResponse, make_envelope, make_response


class MockHttp:
    def __init__(self) -> None:
        self.last_url = ""
        self.last_kwargs: dict[str, object] = {}

    def get(self, url: str, **kwargs: object) -> object:
        self.last_url = url
        self.last_kwargs = dict(kwargs)
        if "/download/" in url:
            return MockResponse(content=b"pdf")
        return make_response(make_envelope([]))

    def put(self, url: str, **kwargs: object) -> object:
        self.last_url = url
        self.last_kwargs = dict(kwargs)
        return make_response(make_envelope([]))


class TestSignerDocumentResource:
    def test_current_uses_documented_endpoint(self) -> None:
        http = MockHttp()
        resource = SignerDocumentResource(http)

        resource.current("signer-1", "code")

        assert http.last_url == "signers/signer-1/document"
        assert http.last_kwargs["params"] == {"signer-access-code": "code"}

    def test_list_combines_filters_and_access_code(self) -> None:
        http = MockHttp()
        resource = SignerDocumentResource(http)

        resource.list("signer-1", "code", {"per_page": 20})

        assert http.last_url == "signers/signer-1/documents"
        assert http.last_kwargs["params"] == {
            "per-page": 20,
            "signer-access-code": "code",
        }

    def test_sign_and_decline_multiple_use_documented_endpoints(self) -> None:
        http = MockHttp()
        resource = SignerDocumentResource(http)

        resource.sign_multiple(["doc-1"], "code")
        assert http.last_url == "signers/documents/sign-multiple"
        assert http.last_kwargs["json"] == {"document_ids": ["doc-1"]}

        resource.decline_multiple(["doc-1"], "No", "code")
        assert http.last_url == "signers/documents/decline-multiple"
        assert http.last_kwargs["json"] == {
            "document_ids": ["doc-1"],
            "decline_reason": "No",
        }

    def test_download_returns_binary_document(self) -> None:
        http = MockHttp()
        resource = SignerDocumentResource(http)

        content = resource.download("signer-1", "doc-1", "code", "original")

        assert http.last_url == "signers/signer-1/documents/doc-1/download/original"
        assert content == b"pdf"
