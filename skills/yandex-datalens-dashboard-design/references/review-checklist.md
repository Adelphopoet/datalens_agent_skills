# Review Checklist

Use this checklist before shipping, reviewing, or refactoring a Yandex DataLens dashboard.

## Business Fit

- The dashboard states the decision or workflow it supports.
- The audience and usage cadence are known.
- Every KPI has an owner and action path.
- The top screen answers status before detail.
- Each tab has one main question.

## Metric Quality

- Dataset grain is written down.
- Shared metrics live at dataset level or upstream in the mart.
- Each metric has formula, aggregation, unit, denominator, filters, and freshness.
- Period comparisons use consistent calendars and time zones.
- Zero, null, late-arriving data, and partial periods are handled explicitly.
- LOD calculations are validated against source SQL or controlled samples.

## Data Model

- Source tables are shaped for analytics, not raw app transactions.
- Heavy joins, parsing, and enrichment are done upstream where practical.
- Field names are business-readable and include units where needed.
- Data types are explicit in the source.
- Large dashboards have safe defaults that avoid full-source scans.
- Connection permissions are read-only and least-privilege.

## DataLens Mechanics

- Selector scope is intentional: global, tab, or local.
- Cross-dataset selectors use aliases and target fields exist in each dataset.
- Chart-level filters are not accidentally disabled by selectors on the same field.
- Chart-by-chart filtering uses dimensions that actually participate in filtering.
- Parameter names avoid reserved keys and are documented.
- Dashboard settings are reviewed: visible-only chart loading, concurrent widget limit, loading priority, auto-update.
- Mobile/widget display order is checked.

## Visual Design

- Chart type matches the analytical task.
- Colors are semantic and consistent across tabs.
- Important comparisons are visually easy: position and length before area and angle.
- Axes, units, labels, and titles make the reading unambiguous.
- Legends, gridlines, borders, and labels are removed when redundant.
- The page does not rely on decoration for structure.
- Empty states, long labels, and Cyrillic text do not break layout.

## Storytelling

- KPI movement has diagnostic charts nearby.
- Drivers are ordered by business importance or contribution.
- Annotations explain known events and data incidents.
- Tables are placed after summary and diagnostic views unless the workflow is operational lookup.
- The dashboard does not ask users to mentally combine too many charts.

## Performance

- Common open path loads in the target latency budget.
- Inspector has been used for slow charts.
- Query count per tab is acceptable.
- High-cardinality charts are aggregated or limited.
- ClickHouse or other OLAP tables are ordered/partitioned for common filters.
- Materialized/pre-aggregated tables exist for billion-row or expensive metrics.
- Auto-refresh frequency does not exceed source freshness.

## Governance

- Workbooks and collections match team ownership.
- Access is group-based where possible.
- Draft/current version flow is understood before editing critical dashboards.
- Dashboard documentation covers definitions, owners, source freshness, caveats, and support.
- Critical dashboards have a validation routine after source/schema changes.

## Final Review Output

When reporting findings, order by severity:

- **P0**: incorrect decision risk, security issue, broken dashboard.
- **P1**: misleading metric, major performance issue, major UX blocker.
- **P2**: inconsistent behavior, maintainability issue, moderate UX issue.
- **P3**: polish, naming, minor layout cleanup.
