---
name: yandex-datalens-dashboard-design
description: Use when designing, planning, building, or reviewing Yandex DataLens dashboards, datasets, charts, selectors, calculated fields, dashboard performance, BI UX, data storytelling, governance, or executive/operational analytics pages. Use yandex-datalens-api as an additional skill only when actual Public API automation is required.
---

# Yandex DataLens Dashboard Design

## Workflow

Use this skill when the task is to create or improve an analytical solution in Yandex DataLens, not merely call the API.

1. Clarify the business decision first: audience, cadence, decisions, actions, KPI definitions, freshness, and acceptable latency.
2. Design the data foundation before charts: grain, source tables, joins, semantic fields, permissions, and reusable measures.
3. Build a dashboard narrative: top-level status, diagnostics, and drill-down detail.
4. Choose visualizations by analytical task, not by novelty.
5. Tune performance as a product requirement: DataLens queries the source, so slow source design becomes a slow dashboard.
6. Finish with a review checklist and explicit tradeoffs.

## Read References As Needed

- Read `references/technical-foundation.md` for DataLens-specific dataset, calculations, parameters, selectors, cross-filtering, performance, versioning, and governance rules.
- Read `references/design-storytelling.md` for dashboard UX, visual hierarchy, chart choice, color, text, and data storytelling guidance.
- Read `references/review-checklist.md` before final review, handoff, or critique of a dashboard.

## Senior BI Defaults

- Start every dashboard with a written metric contract: metric name, formula, grain, filters, owner, update frequency, and known caveats.
- Prefer dataset-level calculated fields for shared metrics. Use chart-level calculations only for local presentation logic or one-off analysis.
- Prefer a clean analytical model in the source over complex live joins and heavy formulas in DataLens.
- Keep one dashboard tab focused on one question. Split by workflow or audience when the page starts mixing unrelated decisions.
- Use selectors deliberately. Every global selector is a query multiplier and a cognitive tax.
- Treat performance, permissions, and definitions as part of dashboard design, not as cleanup.

## Output Shape

When proposing or reviewing a dashboard, provide:

- **Purpose**: the decision the dashboard supports.
- **Data model**: grain, source shape, key dimensions, measures, and ownership.
- **Layout**: tabs, sections, selector scope, and interaction model.
- **Charts**: chart types with rationale.
- **Performance plan**: source optimizations, defaults, widget loading settings, and expected bottlenecks.
- **Governance**: access model, versioning, documentation, and validation.
- **Risks**: assumptions that can break the dashboard or mislead users.

## Red Flags

- A dashboard starts from chart inventory instead of business questions.
- The same metric is calculated differently across charts.
- The dataset grain is not stated.
- Selectors default to "all data" on large tables.
- Charts rely on live joins or calculated fields that should be materialized upstream.
- KPI colors, units, date ranges, or denominator logic change between tabs.
- The first screen cannot answer "are we okay?" within a few seconds.
- A decorative trend such as glassmorphism makes the dashboard less legible.
