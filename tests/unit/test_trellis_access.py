import json
from unittest.mock import patch

import httpx

from movie_factory.providers import trellis_access as p
from movie_factory.settings import safe_settings


def test_missing_never_calls():
    with patch.object(p, "load_token", return_value=""), patch.object(p.httpx, "Client") as client:
        assert p.check(".")["state"] == "CREDENTIAL_MISSING"
        client.assert_not_called()


def test_access_and_secret_exclusion():
    secret = "hf_private_test_credential"
    for status, expected in [(200, "ACCESS_CONFIRMED"), (302, "REDIRECT_REQUIRES_VERIFICATION"),
                             (401, "ACCESS_DENIED_OR_UNAVAILABLE"), (403, "ACCESS_DENIED_OR_UNAVAILABLE")]:
        def handle(request):
            assert request.url.host == "huggingface.co"
            assert request.headers["Authorization"] == "Bearer " + secret
            return httpx.Response(status, text=secret, headers={"Location": "https://example.com/" + secret})
        with patch.object(p, "load_token", return_value=secret), httpx.Client(transport=httpx.MockTransport(handle)) as client:
            result = p.check(".", client=client)
        assert result["state"] == expected
        assert secret not in json.dumps(result)
    assert safe_settings({"HF_TOKEN": secret}) == {"HF_TOKEN": "<set>"}


def test_network_error_redacted():
    def handle(request):
        raise httpx.ConnectError("secret response", request=request)
    with patch.object(p, "load_token", return_value="hf_test"), httpx.Client(transport=httpx.MockTransport(handle)) as client:
        result = p.check(".", client=client)
    assert result["state"] == "NETWORK_ERROR"
    assert "secret" not in json.dumps(result)
