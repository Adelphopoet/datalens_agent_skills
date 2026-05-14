---
name: yandex-datalens-api
description: Use when automating Yandex DataLens Public API/RPC operations, including IAM authentication and API-level work with workbooks, datasets, connections, dashboards, charts, embeds, exports, and access bindings. Do not use for dashboard storytelling, BI analysis, visual design, or non-API Yandex Cloud work unless the task specifically requires DataLens API calls.
---

# Yandex DataLens API

## Workflow

Use this skill for the Yandex DataLens cloud Public API at `https://api.datalens.tech`.

1. Read `references/api.md` to find the RPC method and schema names.
2. Use the method table's required fields, extra headers, and request body skeleton before writing payloads.
3. Read `references/openapi.json` when exact nested request or response fields are needed.
4. Read `references/iam.md` when IAM token creation or auth setup is involved.
5. Resolve the skill directory before running bundled scripts. In Claude Code, use `cd "$CLAUDE_SKILL_DIR"`. In other agents, use the directory containing this `SKILL.md`.
6. Prefer `uv run scripts/datalens_cli.py` for repeatable API calls and schema inspection. Use `python scripts/datalens_cli.py` only when `uv` is unavailable and optional IAM dependencies are already installed.

## API Rules

- All DataLens methods in the bundled spec are `POST /rpc/<method>`.
- Required headers for API calls:
  - `x-yacloud-subjecttoken: <TOKEN>` by default. This matches the OpenMetadata DataLens connector.
  - `x-dl-org-id: <ORG_ID>`
  - `x-dl-api-version: 1`
  - `Content-Type: application/json`
- `Authorization: Bearer <TOKEN>` is available only when `--auth-header Authorization` or `DATALENS_AUTH_HEADER=Authorization` is set.
- Do not print, log, commit, or paste real IAM tokens, service account keys, passwords, connection secrets, OAuth tokens, or secret headers.
- Treat experimental methods marked with `Experimental` in the OpenAPI summary as unstable.

## CLI Quick Start

Run commands from this skill directory. In Claude Code:

```bash
cd "$CLAUDE_SKILL_DIR"
```

List methods:

```bash
uv run scripts/datalens_cli.py methods
uv run scripts/datalens_cli.py methods --tag Workbook
```

Inspect schemas:

```bash
uv run scripts/datalens_cli.py schema getWorkbook --request
uv run scripts/datalens_cli.py schema getWorkbook --response
uv run scripts/datalens_cli.py example getWorkbook
```

Call an RPC method:

```bash
export DATALENS_API_TOKEN="..."
export DATALENS_ORG_ID="..."
uv run scripts/datalens_cli.py rpc getWorkbooksList --body '{}'
```

Pass optional API headers when a method needs them:

```bash
uv run scripts/datalens_cli.py rpc getDataset --header x-dl-audit-mode=true --body '{"datasetId":"..."}'
```

Refresh bundled API references:

```bash
uv run scripts/datalens_cli.py refresh-spec
uv run scripts/datalens_cli.py generate-api-index
```

Create an IAM token from a service account key:

```bash
uv run scripts/datalens_cli.py iam-token --sa-key key.json
```

Or use a federated/user IAM token from the Yandex Cloud CLI:

```bash
yc init --federation-id=<federation_id>
export DATALENS_IAM_TOKEN="$(yc iam create-token)"
```

## Environment

- `DATALENS_API_TOKEN`: existing DataLens/Yandex token sent as `x-yacloud-subjecttoken`.
- `DATALENS_IAM_TOKEN`: existing IAM token from `yc iam create-token` or another trusted flow; also sent as `x-yacloud-subjecttoken` by default.
- `DATALENS_ORG_ID`: DataLens organization ID for `x-dl-org-id`.
- `DATALENS_AUTH_HEADER`: token header; defaults to `x-yacloud-subjecttoken`. Set to `Authorization` for bearer auth.
- `DATALENS_API_URL`: defaults to `https://api.datalens.tech`.
- `DATALENS_API_VERSION`: defaults to `1`.
- `DATALENS_TIMEOUT`: HTTP timeout in seconds; defaults to `30`.
- `YC_SERVICE_ACCOUNT_KEY_FILE`: service account authorized key JSON for IAM token creation.
