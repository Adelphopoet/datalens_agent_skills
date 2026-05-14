#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO


DEFAULT_API_URL = "https://api.datalens.tech"
DEFAULT_SPEC_URL = "https://api.datalens.tech/json/"
DEFAULT_API_VERSION = "1"
DEFAULT_AUTH_HEADER = "x-yacloud-subjecttoken"
DEFAULT_TIMEOUT = 30.0
IAM_AUDIENCE = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
SENSITIVE_KEY_RE = re.compile(
    r"(authorization|x-yacloud-subjecttoken|private_key|token|password|secret|access_token)",
    re.IGNORECASE,
)
HEADER_SECRET_RE = re.compile(
    r"(?im)^(\s*(?:authorization|x-yacloud-subjecttoken)\s*[:=]\s*)(.+)$"
)
JSON_SECRET_RE = re.compile(
    r'("([^"]*(?:authorization|x-yacloud-subjecttoken|private_key|token|password|secret|access_token)[^"]*)"\s*:\s*)'
    r'("([^"\\]|\\.)*"|[^,\n\r}\]]+)',
    re.IGNORECASE,
)


class CLIError(Exception):
    pass


def default_openapi_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "openapi.json"


def default_api_index_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "api.md"


def load_openapi(path: str | Path | None = None) -> dict[str, Any]:
    spec_path = Path(path) if path else default_openapi_path()
    with spec_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_openapi(spec: dict[str, Any], path: str | Path | None = None) -> None:
    spec_path = Path(path) if path else default_openapi_path()
    with spec_path.open("w", encoding="utf-8") as fh:
        json.dump(spec, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def spec_sha256(spec: dict[str, Any]) -> str:
    raw = json.dumps(spec, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def rpc_path(method: str) -> str:
    method = method.strip()
    if not method:
        raise CLIError("RPC method is empty")
    if method.startswith("/rpc/"):
        return method
    return f"/rpc/{method}"


def get_operation(spec: dict[str, Any], method: str) -> tuple[str, dict[str, Any]]:
    path = rpc_path(method)
    operation = spec.get("paths", {}).get(path, {}).get("post")
    if not operation:
        raise CLIError(f"Unknown DataLens RPC method: {method}")
    return path, operation


def schema_name(schema: dict[str, Any]) -> str:
    ref = schema.get("$ref")
    return ref.rsplit("/", 1)[-1] if isinstance(ref, str) else ""


def resolve_schema_ref(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    name = schema_name(schema)
    if not name:
        return schema
    resolved = spec.get("components", {}).get("schemas", {}).get(name)
    return resolved if isinstance(resolved, dict) else schema


def merge_all_of_schema(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    schema = resolve_schema_ref(spec, schema)
    if "allOf" not in schema:
        return schema

    merged: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    for part in schema.get("allOf", []):
        if not isinstance(part, dict):
            continue
        resolved = merge_all_of_schema(spec, part)
        if isinstance(resolved.get("properties"), dict):
            merged["properties"].update(resolved["properties"])
        if isinstance(resolved.get("required"), list):
            merged["required"].extend(resolved["required"])
    merged["required"] = sorted(set(merged["required"]))
    return merged


def schema_for_operation(
    spec: dict[str, Any], method: str, *, response: bool = False
) -> dict[str, Any]:
    _, operation = get_operation(spec, method)
    if response:
        schema = (
            operation.get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )
    else:
        schema = (
            operation.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )
    if not isinstance(schema, dict):
        return {}
    name = schema_name(schema)
    if name:
        resolved = spec.get("components", {}).get("schemas", {}).get(name)
        if isinstance(resolved, dict):
            result = dict(resolved)
            result["x-datalens-schema-name"] = name
            return result
    return schema


def operation_extra_headers(operation: dict[str, Any]) -> list[str]:
    headers: list[str] = []
    for parameter in operation.get("parameters", []):
        if "$ref" in parameter:
            continue
        if parameter.get("in") == "header" and parameter.get("name") != "x-dl-api-version":
            headers.append(str(parameter.get("name")))
    return headers


def request_required_fields(spec: dict[str, Any], method: str) -> list[str]:
    schema = merge_all_of_schema(spec, schema_for_operation(spec, method))
    required = schema.get("required")
    if isinstance(required, list) and required:
        return [str(item) for item in required]
    if isinstance(schema.get("oneOf"), list) or isinstance(schema.get("anyOf"), list):
        return ["variant-specific"]
    return []


def placeholder_for_schema(
    spec: dict[str, Any],
    schema: dict[str, Any],
    *,
    include_optional: bool = False,
    seen_refs: set[str] | None = None,
) -> Any:
    seen_refs = seen_refs or set()
    ref = schema.get("$ref")
    if isinstance(ref, str):
        if ref in seen_refs:
            return {}
        seen_refs.add(ref)
    schema = merge_all_of_schema(spec, schema)

    if "const" in schema:
        return schema["const"]
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        return enum[0]

    for union_key in ("oneOf", "anyOf"):
        variants = schema.get(union_key)
        if isinstance(variants, list) and variants:
            non_null = [
                item
                for item in variants
                if isinstance(item, dict) and item.get("type") != "null"
            ]
            return placeholder_for_schema(
                spec,
                non_null[0] if non_null else variants[0],
                include_optional=include_optional,
                seen_refs=seen_refs,
            )

    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        schema_type = next((item for item in schema_type if item != "null"), schema_type[0])

    if schema_type == "object" or isinstance(schema.get("properties"), dict):
        properties = schema.get("properties") or {}
        required = set(schema.get("required") or [])
        keys = set(properties) if include_optional else required
        return {
            key: placeholder_for_schema(
                spec,
                value,
                include_optional=include_optional,
                seen_refs=set(seen_refs),
            )
            for key, value in properties.items()
            if key in keys
        }
    if schema_type == "array":
        return []
    if schema_type == "boolean":
        return False
    if schema_type in {"integer", "number"}:
        return 0
    if schema_type == "null":
        return None
    return "<string>"


def request_body_example(
    spec: dict[str, Any], method: str, *, include_optional: bool = False
) -> dict[str, Any]:
    schema = schema_for_operation(spec, method)
    if not schema:
        return {}
    example = placeholder_for_schema(spec, schema, include_optional=include_optional)
    if not isinstance(example, dict):
        raise CLIError(f"Request body for {method} is not a JSON object")
    return example


def compact_body_skeleton(spec: dict[str, Any], method: str, *, max_length: int = 120) -> str:
    try:
        text = json.dumps(request_body_example(spec, method), ensure_ascii=False, separators=(",", ":"))
    except CLIError:
        return f"run datalens_cli.py example {method}"
    return text if len(text) <= max_length else f"run datalens_cli.py example {method}"


def list_methods(spec: dict[str, Any], tag: str | None = None) -> list[dict[str, str]]:
    methods: list[dict[str, str]] = []
    for path, item in sorted(spec.get("paths", {}).items()):
        operation = item.get("post", {})
        tags = operation.get("tags") or ["Other"]
        operation_tag = str(tags[0])
        if tag and operation_tag != tag:
            continue
        request_schema = schema_name(
            operation.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        response_schema = schema_name(
            operation.get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        methods.append(
            {
                "method": path.removeprefix("/rpc/"),
                "path": path,
                "tag": operation_tag,
                "summary": str(operation.get("summary") or ""),
                "description": str(operation.get("description") or ""),
                "extra_headers": ", ".join(operation_extra_headers(operation)),
                "required_fields": ", ".join(request_required_fields(spec, path)),
                "body_skeleton": compact_body_skeleton(spec, path.removeprefix("/rpc/")),
                "request_schema": request_schema,
                "response_schema": response_schema,
            }
        )
    return methods


def clean_summary(summary: str) -> str:
    return summary.replace("🚧 ", "").strip()


def markdown_cell(value: str) -> str:
    value = value or "-"
    return value.replace("|", "\\|").replace("\n", " ")


def markdown_code_cell(value: str) -> str:
    value = markdown_cell(value)
    return value if value == "-" else f"`{value}`"


def render_api_index(
    spec: dict[str, Any],
    *,
    source_url: str = DEFAULT_SPEC_URL,
    generated_at: str | None = None,
) -> str:
    generated_at = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    methods = list_methods(spec)
    lines = [
        "# DataLens Public API Index",
        "",
        f"Source: `references/openapi.json` from `{source_url}`.",
        f"Generated: `{generated_at}`.",
        f"OpenAPI SHA256: `{spec_sha256(spec)}`.",
        "",
        "All methods are `POST /rpc/<method>` and require `x-yacloud-subjecttoken`, `x-dl-org-id`, `x-dl-api-version: 1`, and `Content-Type: application/json`. The CLI can also send `Authorization: Bearer <TOKEN>` when `--auth-header Authorization` is used.",
        "",
        "Use `scripts/datalens_cli.py example <method>` for full request skeletons. The table below shows top-level required fields, variant-specific bodies, extra headers, and compact body skeletons when they fit.",
        "",
        f"Total RPC methods: {len(methods)}.",
        "",
    ]

    current_tag: str | None = None
    for item in sorted(methods, key=lambda method: (method["tag"], method["method"])):
        if item["tag"] != current_tag:
            if current_tag is not None:
                lines.append("")
            current_tag = item["tag"]
            lines.extend(
                [
                    f"## {current_tag}",
                    "",
                    "| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |",
                    "| --- | --- | --- | --- | --- | --- | --- |",
                ]
            )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{markdown_cell(item['method'])}`",
                    markdown_cell(clean_summary(item["summary"])),
                    markdown_code_cell(item["required_fields"]),
                    markdown_code_cell(item["extra_headers"]),
                    markdown_code_cell(item["body_skeleton"]),
                    markdown_code_cell(item["request_schema"]),
                    markdown_code_cell(item["response_schema"]),
                ]
            )
            + " |"
        )
        if item["description"]:
            lines.append(
                f"| | Description: {markdown_cell(clean_summary(item['description']))} | | | | | |"
            )
    lines.append("")
    return "\n".join(lines)


def read_service_account_key(path: str | Path) -> dict[str, str]:
    with Path(path).open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    required = ["id", "service_account_id", "private_key"]
    missing = [key for key in required if not raw.get(key)]
    if missing:
        raise CLIError(f"Service account key is missing: {', '.join(missing)}")
    return {key: raw[key] for key in required}


def redact_data(data: Any) -> Any:
    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            key_text = str(key)
            redacted[key] = "<redacted>" if SENSITIVE_KEY_RE.search(key_text) else redact_data(value)
        return redacted
    if isinstance(data, list):
        return [redact_data(item) for item in data]
    return data


def redact_secrets(text: str) -> str:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        redacted = HEADER_SECRET_RE.sub(r"\1<redacted>", text)
        return JSON_SECRET_RE.sub(r'\1"<redacted>"', redacted)
    return json.dumps(redact_data(parsed), ensure_ascii=False, separators=(",", ":"))


def create_jwt_for_service_account(sa_key: dict[str, str]) -> str:
    try:
        import jwt
    except ImportError as exc:
        raise CLIError("Install PyJWT and cryptography to create service account JWTs") from exc

    now = int(time.time())
    payload = {
        "aud": IAM_AUDIENCE,
        "iss": sa_key["service_account_id"],
        "iat": now,
        "exp": now + 3600,
    }
    return jwt.encode(
        payload,
        sa_key["private_key"],
        algorithm="PS256",
        headers={"kid": sa_key["id"]},
    )


def create_iam_token_from_service_account_key(path: str | Path) -> str:
    try:
        import yandexcloud
        from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
        from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub
    except ImportError as exc:
        raise CLIError("Install yandexcloud to exchange service account JWTs for IAM tokens") from exc

    sa_key = read_service_account_key(path)
    token_jwt = create_jwt_for_service_account(sa_key)
    sdk = yandexcloud.SDK(service_account_key=sa_key)
    iam_service = sdk.client(IamTokenServiceStub)
    iam_token = iam_service.Create(CreateIamTokenRequest(jwt=token_jwt))
    return iam_token.iam_token


def get_iam_token(args: argparse.Namespace) -> str:
    if getattr(args, "iam_token", None):
        return args.iam_token
    env_token = os.getenv("DATALENS_IAM_TOKEN")
    if env_token:
        return env_token
    env_token = os.getenv("DATALENS_API_TOKEN")
    if env_token:
        return env_token
    sa_key = getattr(args, "sa_key", None) or os.getenv("YC_SERVICE_ACCOUNT_KEY_FILE")
    if sa_key:
        return create_iam_token_from_service_account_key(sa_key)
    raise CLIError(
        "Set DATALENS_IAM_TOKEN/DATALENS_API_TOKEN or provide "
        "--sa-key/YC_SERVICE_ACCOUNT_KEY_FILE"
    )


def get_org_id(args: argparse.Namespace) -> str:
    org_id = getattr(args, "org_id", None) or os.getenv("DATALENS_ORG_ID")
    if not org_id:
        raise CLIError("Set DATALENS_ORG_ID or provide --org-id")
    return org_id


def build_headers(args: argparse.Namespace) -> dict[str, str]:
    token = get_iam_token(args)
    auth_header = (
        getattr(args, "auth_header", None)
        or os.getenv("DATALENS_AUTH_HEADER")
        or DEFAULT_AUTH_HEADER
    )
    auth_value = f"Bearer {token}" if auth_header.lower() == "authorization" else token
    headers = {
        auth_header: auth_value,
        "x-dl-org-id": get_org_id(args),
        "x-dl-api-version": getattr(args, "api_version", None)
        or os.getenv("DATALENS_API_VERSION", DEFAULT_API_VERSION),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    for raw_header in getattr(args, "header", None) or []:
        if ":" in raw_header:
            name, value = raw_header.split(":", 1)
        elif "=" in raw_header:
            name, value = raw_header.split("=", 1)
        else:
            raise CLIError(f"Header must be NAME=VALUE or NAME:VALUE: {raw_header}")
        name = name.strip()
        if not name:
            raise CLIError(f"Header name is empty: {raw_header}")
        headers[name] = value.strip()
    return headers


def parse_json_body(args: argparse.Namespace, stdin: TextIO = sys.stdin) -> dict[str, Any]:
    body: str
    if getattr(args, "body", None) is not None:
        body = stdin.read() if args.body == "-" else args.body
    elif getattr(args, "body_file", None):
        if args.body_file == "-":
            body = stdin.read()
        else:
            body = Path(args.body_file).read_text(encoding="utf-8")
    else:
        body = "{}"
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise CLIError(f"Request body is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise CLIError("Request body must be a JSON object")
    return parsed


def print_json(data: Any, stdout: TextIO = sys.stdout) -> None:
    json.dump(data, stdout, ensure_ascii=False, indent=2, sort_keys=True)
    stdout.write("\n")


def request_url(args: argparse.Namespace, path: str) -> str:
    base_url = getattr(args, "api_url", None) or os.getenv("DATALENS_API_URL", DEFAULT_API_URL)
    return base_url.rstrip("/") + path


def get_timeout(args: argparse.Namespace) -> float:
    raw_timeout = getattr(args, "timeout", None) or os.getenv("DATALENS_TIMEOUT") or DEFAULT_TIMEOUT
    try:
        timeout = float(raw_timeout)
    except (TypeError, ValueError) as exc:
        raise CLIError(f"Timeout must be a positive number: {raw_timeout}") from exc
    if timeout <= 0:
        raise CLIError(f"Timeout must be a positive number: {raw_timeout}")
    return timeout


def call_rpc(
    args: argparse.Namespace,
    *,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    spec = load_openapi(getattr(args, "openapi", None))
    path, _ = get_operation(spec, args.method)
    body = parse_json_body(args, stdin=stdin)
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        request_url(args, path),
        data=payload,
        headers=build_headers(args),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=get_timeout(args)) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        request_id = exc.headers.get("x-request-id") if exc.headers else None
        stderr.write(f"HTTP {exc.code} calling {path}\n")
        if request_id:
            stderr.write(f"x-request-id: {request_id}\n")
        if raw:
            stderr.write(redact_secrets(raw).rstrip() + "\n")
        return 1
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        stderr.write(f"Network error calling {path}: {exc}\n")
        return 1
    if raw:
        try:
            print_json(json.loads(raw), stdout=stdout)
        except json.JSONDecodeError:
            stdout.write(raw)
            if not raw.endswith("\n"):
                stdout.write("\n")
    return 0


def command_methods(args: argparse.Namespace) -> int:
    spec = load_openapi(args.openapi)
    methods = list_methods(spec, tag=args.tag)
    if args.json:
        print_json(methods)
        return 0
    for item in methods:
        print(
            "\t".join(
                [
                    item["tag"],
                    item["method"],
                    item["summary"],
                    item["required_fields"],
                    item["extra_headers"],
                    item["request_schema"],
                    item["response_schema"],
                ]
            )
        )
    return 0


def command_schema(args: argparse.Namespace) -> int:
    spec = load_openapi(args.openapi)
    print_json(schema_for_operation(spec, args.method, response=args.response))
    return 0


def command_example(args: argparse.Namespace) -> int:
    spec = load_openapi(args.openapi)
    print_json(request_body_example(spec, args.method, include_optional=args.include_optional))
    return 0


def command_iam_token(args: argparse.Namespace) -> int:
    print(get_iam_token(args))
    return 0


def fetch_openapi_spec(url: str, *, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise CLIError("Downloaded OpenAPI spec is not a JSON object")
    return parsed


def command_generate_api_index(args: argparse.Namespace) -> int:
    spec = load_openapi(args.openapi)
    output = Path(args.output) if args.output else default_api_index_path()
    output.write_text(render_api_index(spec, source_url=args.source_url), encoding="utf-8")
    print(f"Wrote {output}")
    return 0


def command_refresh_spec(args: argparse.Namespace) -> int:
    try:
        spec = fetch_openapi_spec(args.spec_url, timeout=get_timeout(args))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise CLIError(f"Failed to fetch OpenAPI spec from {args.spec_url}: {exc}") from exc

    openapi_path = Path(args.openapi) if args.openapi else default_openapi_path()
    api_index_path = Path(args.api_index) if args.api_index else default_api_index_path()
    write_openapi(spec, openapi_path)
    api_index_path.write_text(
        render_api_index(spec, source_url=args.spec_url),
        encoding="utf-8",
    )
    print(f"Wrote {openapi_path}")
    print(f"Wrote {api_index_path}")
    print(f"OpenAPI SHA256: {spec_sha256(spec)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Yandex DataLens Public API helper")
    parser.add_argument("--openapi", help="Path to OpenAPI JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    iam = subparsers.add_parser("iam-token", help="Print an IAM token")
    iam.add_argument("--iam-token", help="Existing IAM token")
    iam.add_argument("--sa-key", help="Service account authorized key JSON")
    iam.set_defaults(func=command_iam_token)

    methods = subparsers.add_parser("methods", help="List DataLens RPC methods")
    methods.add_argument("--tag", help="Filter by OpenAPI tag")
    methods.add_argument("--json", action="store_true", help="Print JSON")
    methods.set_defaults(func=command_methods)

    schema = subparsers.add_parser("schema", help="Print request or response schema")
    schema.add_argument("method", help="RPC method, for example getWorkbook")
    schema_group = schema.add_mutually_exclusive_group()
    schema_group.add_argument("--request", action="store_true", help="Print request schema")
    schema_group.add_argument("--response", action="store_true", help="Print response schema")
    schema.set_defaults(func=command_schema)

    example = subparsers.add_parser("example", help="Print request body skeleton")
    example.add_argument("method", help="RPC method, for example getWorkbook")
    example.add_argument(
        "--include-optional",
        action="store_true",
        help="Include optional request fields in the generated body",
    )
    example.set_defaults(func=command_example)

    generate_index = subparsers.add_parser(
        "generate-api-index",
        help="Regenerate references/api.md from an OpenAPI JSON file",
    )
    generate_index.add_argument("--output", help="Path to write api.md")
    generate_index.add_argument(
        "--source-url",
        default=DEFAULT_SPEC_URL,
        help="Source URL to record in the generated index",
    )
    generate_index.set_defaults(func=command_generate_api_index)

    refresh = subparsers.add_parser(
        "refresh-spec",
        help="Download OpenAPI JSON and regenerate references/api.md",
    )
    refresh.add_argument("--spec-url", default=DEFAULT_SPEC_URL)
    refresh.add_argument("--api-index", help="Path to write api.md")
    refresh.add_argument(
        "--timeout",
        default=os.getenv("DATALENS_TIMEOUT", str(DEFAULT_TIMEOUT)),
        help="HTTP timeout in seconds",
    )
    refresh.set_defaults(func=command_refresh_spec)

    rpc = subparsers.add_parser("rpc", help="Call a DataLens RPC method")
    rpc.add_argument("method", help="RPC method, for example getWorkbook")
    body_group = rpc.add_mutually_exclusive_group()
    body_group.add_argument("--body", help="JSON request body, or '-' for stdin")
    body_group.add_argument("--body-file", help="Path to JSON request body, or '-' for stdin")
    rpc.add_argument("--iam-token", help="Existing IAM token")
    rpc.add_argument("--sa-key", help="Service account authorized key JSON")
    rpc.add_argument("--org-id", help="DataLens organization ID")
    rpc.add_argument(
        "--header",
        action="append",
        help="Extra request header as NAME=VALUE or NAME:VALUE. Repeatable.",
    )
    rpc.add_argument(
        "--auth-header",
        default=os.getenv("DATALENS_AUTH_HEADER", DEFAULT_AUTH_HEADER),
        help=(
            "Header used for the DataLens token. Defaults to "
            "x-yacloud-subjecttoken; use Authorization for Bearer auth."
        ),
    )
    rpc.add_argument("--api-url", default=os.getenv("DATALENS_API_URL", DEFAULT_API_URL))
    rpc.add_argument("--api-version", default=os.getenv("DATALENS_API_VERSION", DEFAULT_API_VERSION))
    rpc.add_argument(
        "--timeout",
        default=os.getenv("DATALENS_TIMEOUT", str(DEFAULT_TIMEOUT)),
        help="HTTP timeout in seconds",
    )
    rpc.set_defaults(func=call_rpc)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CLIError as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
