from __future__ import annotations

import argparse
import importlib.util
from email.message import Message
from io import BytesIO, StringIO
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "skills" / "yandex-datalens-api" / "scripts" / "datalens_cli.py"
OPENAPI_PATH = ROOT / "skills" / "yandex-datalens-api" / "references" / "openapi.json"


def load_cli():
    spec = importlib.util.spec_from_file_location("datalens_cli", CLI_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def cli():
    return load_cli()


def test_get_iam_token_prefers_explicit_then_env_then_service_account(cli, monkeypatch):
    args = argparse.Namespace(iam_token="explicit-token", sa_key=None)
    assert cli.get_iam_token(args) == "explicit-token"

    args = argparse.Namespace(iam_token=None, sa_key=None)
    monkeypatch.setenv("DATALENS_IAM_TOKEN", "env-token")
    assert cli.get_iam_token(args) == "env-token"

    monkeypatch.delenv("DATALENS_IAM_TOKEN")
    monkeypatch.setenv("DATALENS_API_TOKEN", "api-token")
    assert cli.get_iam_token(args) == "api-token"

    monkeypatch.delenv("DATALENS_API_TOKEN")
    monkeypatch.setenv("YC_SERVICE_ACCOUNT_KEY_FILE", "key.json")
    monkeypatch.setattr(
        cli,
        "create_iam_token_from_service_account_key",
        lambda path: f"sa-token:{path}",
    )
    assert cli.get_iam_token(args) == "sa-token:key.json"


def test_build_headers_uses_required_datalens_headers(cli, monkeypatch):
    monkeypatch.setenv("DATALENS_IAM_TOKEN", "token")
    monkeypatch.setenv("DATALENS_ORG_ID", "org")
    args = argparse.Namespace(api_version="1")

    headers = cli.build_headers(args)

    assert headers["x-yacloud-subjecttoken"] == "token"
    assert headers["x-dl-org-id"] == "org"
    assert headers["x-dl-api-version"] == "1"
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


def test_build_headers_can_use_authorization_bearer(cli, monkeypatch):
    monkeypatch.setenv("DATALENS_IAM_TOKEN", "token")
    monkeypatch.setenv("DATALENS_ORG_ID", "org")
    args = argparse.Namespace(api_version="1", auth_header="Authorization")

    headers = cli.build_headers(args)

    assert headers["Authorization"] == "Bearer token"
    assert "x-yacloud-subjecttoken" not in headers


def test_build_headers_accepts_extra_headers(cli, monkeypatch):
    monkeypatch.setenv("DATALENS_IAM_TOKEN", "token")
    monkeypatch.setenv("DATALENS_ORG_ID", "org")
    args = argparse.Namespace(
        api_version="1",
        auth_header="x-yacloud-subjecttoken",
        header=["x-dl-audit-mode=true", "x-custom: value"],
    )

    headers = cli.build_headers(args)

    assert headers["x-dl-audit-mode"] == "true"
    assert headers["x-custom"] == "value"


def test_get_timeout_validates_positive_number(cli, monkeypatch):
    args = argparse.Namespace(timeout="2.5")
    assert cli.get_timeout(args) == 2.5

    args = argparse.Namespace(timeout=None)
    monkeypatch.setenv("DATALENS_TIMEOUT", "7")
    assert cli.get_timeout(args) == 7.0

    args = argparse.Namespace(timeout="0")
    with pytest.raises(cli.CLIError, match="positive number"):
        cli.get_timeout(args)


def test_openapi_method_validation(cli):
    spec = cli.load_openapi(OPENAPI_PATH)

    path, operation = cli.get_operation(spec, "getWorkbook")
    assert path == "/rpc/getWorkbook"
    assert operation["summary"] == "Get workbook"

    with pytest.raises(cli.CLIError, match="Unknown DataLens RPC method"):
        cli.get_operation(spec, "noSuchMethod")


def test_request_body_example_uses_required_fields(cli):
    spec = cli.load_openapi(OPENAPI_PATH)

    assert cli.request_required_fields(spec, "getWorkbook") == ["workbookId"]
    assert cli.request_body_example(spec, "getWorkbook") == {"workbookId": "<string>"}
    assert cli.request_body_example(spec, "getWorkbook", include_optional=True) == {
        "includePermissionsInfo": False,
        "workbookId": "<string>",
    }


def test_parse_json_body_from_string_file_and_stdin(cli, tmp_path):
    args = argparse.Namespace(body='{"workbookId": "wb"}', body_file=None)
    assert cli.parse_json_body(args) == {"workbookId": "wb"}

    body_file = tmp_path / "body.json"
    body_file.write_text('{"pageSize": 10}', encoding="utf-8")
    args = argparse.Namespace(body=None, body_file=str(body_file))
    assert cli.parse_json_body(args) == {"pageSize": 10}

    args = argparse.Namespace(body="-", body_file=None)
    stdin = StringIO('{"collectionId": null}')
    assert cli.parse_json_body(args, stdin=stdin) == {"collectionId": None}


def test_call_rpc_reports_http_error(cli, monkeypatch):
    headers = Message()
    headers["x-request-id"] = "request-123"
    error = HTTPError(
        "https://api.datalens.tech/rpc/getWorkbook",
        400,
        "Bad Request",
        headers,
        BytesIO(b'{"message":"bad request","access_token":"secret-token"}'),
    )

    def fake_urlopen(request, timeout):
        assert timeout == 30.0
        raise error

    monkeypatch.setattr(cli.urllib.request, "urlopen", fake_urlopen)
    args = argparse.Namespace(
        openapi=str(OPENAPI_PATH),
        method="getWorkbook",
        body='{"workbookId": "wb"}',
        body_file=None,
        iam_token="token",
        sa_key=None,
        org_id="org",
        auth_header="x-yacloud-subjecttoken",
        api_url="https://api.datalens.tech",
        api_version="1",
        timeout="30",
    )
    stderr = StringIO()

    result = cli.call_rpc(args, stderr=stderr)

    assert result == 1
    text = stderr.getvalue()
    assert "HTTP 400 calling /rpc/getWorkbook" in text
    assert "x-request-id: request-123" in text
    assert '"message":"bad request"' in text
    assert "secret-token" not in text
    assert '"access_token":"<redacted>"' in text


def test_call_rpc_reports_network_error(cli, monkeypatch):
    def fake_urlopen(request, timeout):
        raise URLError("timed out")

    monkeypatch.setattr(cli.urllib.request, "urlopen", fake_urlopen)
    args = argparse.Namespace(
        openapi=str(OPENAPI_PATH),
        method="getWorkbook",
        body='{"workbookId": "wb"}',
        body_file=None,
        iam_token="token",
        sa_key=None,
        org_id="org",
        auth_header="x-yacloud-subjecttoken",
        api_url="https://api.datalens.tech",
        api_version="1",
        timeout="1",
    )
    stderr = StringIO()

    result = cli.call_rpc(args, stderr=stderr)

    assert result == 1
    assert "Network error calling /rpc/getWorkbook" in stderr.getvalue()


def test_render_api_index_includes_generation_metadata(cli):
    spec = cli.load_openapi(OPENAPI_PATH)

    text = cli.render_api_index(
        spec,
        source_url="https://example.test/openapi.json",
        generated_at="2026-05-14T00:00:00+00:00",
    )

    assert "Generated: `2026-05-14T00:00:00+00:00`." in text
    assert "OpenAPI SHA256:" in text
    assert "| `getWorkbook` | Get workbook | `workbookId`" in text
