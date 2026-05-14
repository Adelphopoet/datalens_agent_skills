# IAM Authentication For DataLens

DataLens Public API accepts the token header used by the OpenMetadata DataLens connector:

```text
x-yacloud-subjecttoken: <TOKEN>
```

Also send the organization header:

```text
x-dl-org-id: <ORG_ID>
```

## Preferred v1 Paths

Use one of these:

- Existing DataLens/Yandex token: set `DATALENS_API_TOKEN`.
- Existing IAM token from Yandex Cloud CLI: set `DATALENS_IAM_TOKEN`.
- Service account authorized key JSON: set `YC_SERVICE_ACCOUNT_KEY_FILE` or pass `--sa-key`.

The CLI sends tokens as `x-yacloud-subjecttoken` by default. To force bearer auth, pass
`--auth-header Authorization` or set `DATALENS_AUTH_HEADER=Authorization`.

## Federated User Flow With YC CLI

Use this when the user authenticates through an organization identity federation and needs an interactive, short-lived token:

```bash
yc init --federation-id=<federation_id>
export DATALENS_IAM_TOKEN="$(yc iam create-token)"
```

Then call DataLens:

```bash
export DATALENS_ORG_ID="<org_id>"
uv run scripts/datalens_cli.py rpc getWorkbooksList --body '{}'
```

This flow is for interactive user work. Do not use it as the default for unattended automation; use a service account key or managed secret flow instead.

## Service Account Key Flow

Use `uv run scripts/datalens_cli.py ...` from the skill directory. In Claude Code, run `cd "$CLAUDE_SKILL_DIR"` first. The script includes inline `uv` metadata for IAM dependencies.

Install dependencies manually only when running without `uv`:

```bash
python -m pip install yandexcloud PyJWT cryptography
```

Create an authorized key with `yc`:

```bash
yc iam key create --output key.json --service-account-name <service_account_name>
```

Create an IAM token:

```bash
uv run scripts/datalens_cli.py iam-token --sa-key key.json
```

The CLI signs a JWT with `PS256`, then exchanges it through Yandex Cloud IAM using the `yandexcloud` SDK.

## Token Lifetime

IAM token lifetime is limited. Request a fresh token for long-running automation instead of storing one permanently.

## Security

- Never commit service account key JSON files.
- Never echo real tokens in examples, logs, tickets, or docs.
- Prefer env vars or secret storage for automation.
- Redact `Authorization`, `x-yacloud-subjecttoken`, `private_key`, `token`, `password`, `secret_headers`, and `access_token` values before sharing payloads.

## Sources

- DataLens Public API: `https://yandex.cloud/en/docs/datalens/operations/api-start`
- Federated user CLI authentication: `https://yandex.cloud/en/docs/cli/operations/authentication/federated-user`
- IAM token for federated account: `https://yandex.cloud/en/docs/iam/operations/iam-token/create-for-federation`
- `yc iam create-token` CLI reference: `https://yandex.cloud/en/docs/cli/cli-ref/iam/cli-ref/v0/create-token`
- IAM token for service account: `https://yandex.cloud/en/docs/iam/operations/iam-token/create-for-sa`
- Yandex Cloud Python SDK: `https://github.com/yandex-cloud/python-sdk`
