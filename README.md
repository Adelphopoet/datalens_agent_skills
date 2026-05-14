# DataLens Agent Skills

Скиллы для работы агентов с Yandex DataLens: API-автоматизация, проектирование дашбордов, BI UX, производительность и governance.

## Skills

### `yandex-datalens-api`

Для автоматизации Yandex DataLens Public API/RPC:

- IAM/auth setup.
- Workbooks, datasets, connections, dashboards, charts, embeds, exports.
- Access bindings.
- CLI-хелпер: `skills/yandex-datalens-api/scripts/datalens_cli.py`.

### `yandex-datalens-dashboard-design`

Для проектирования и ревью DataLens-дашбордов:

- data foundation: grain, joins, semantic layer, calculated fields, LOD, parameters;
- dashboard UX: layout, selectors, chart filtering, tabs, mobile order;
- performance: source tuning, defaults, visible widgets, concurrent widget limits;
- storytelling: KPI hierarchy, diagnostics, drill-down, annotations;
- governance: workbooks, collections, access, versioning, documentation.

## Structure

```text
skills/
  <skill-name>/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
tests/
```

`SKILL.md` должен быть коротким входом в скилл. Подробности клади в `references/`, повторяемую механику - в `scripts/`.

## Development

Run tests:

```bash
pytest -q
```

Useful API commands:

```bash
python skills/yandex-datalens-api/scripts/datalens_cli.py methods
python skills/yandex-datalens-api/scripts/datalens_cli.py schema getWorkbook --request
```

## Rules

- Не коммить токены, IAM keys, OAuth secrets, пароли и connection secrets.
- Для DataLens API используй `yandex-datalens-api`.
- Для дизайна, сторителлинга и ревью дашбордов используй `yandex-datalens-dashboard-design`.
- Для критичных дашбордов проверяй не только визуал, но и grain, формулы, фильтры, latency и права доступа.
