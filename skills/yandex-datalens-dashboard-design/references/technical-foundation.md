# Technical Foundation

## DataLens Operating Model

- DataLens is a direct-query BI tool: charts and selectors execute queries against the connected source, and calculated fields are generally pushed to the source. Design the source for dashboard access.
- Use read-only service accounts and least-privilege access for dashboard connections.
- For high-load analytical dashboards, prefer OLAP-ready sources and pre-shaped analytical marts. ClickHouse is usually the first-class fit when data volume and interactivity matter.
- Use the chart Inspector to inspect generated SQL, source timing, and rendering bottlenecks before guessing.

## Dataset Design

Define the dataset contract before building charts:

- **Grain**: one sentence that states what a single row represents.
- **Keys**: primary/business keys and join keys.
- **Measures**: additive, semi-additive, non-additive, and their default aggregation.
- **Dimensions**: business names, units, formatting, hierarchy, and null handling.
- **Freshness**: source update cadence and dashboard auto-update expectations.
- **Security**: who can read source rows, objects, workbooks, and collections.

Prefer:

- Denormalized marts or star schemas for recurring dashboards.
- Business-readable field names over raw technical names.
- Explicit DB-side data types, especially dates and numbers.
- DB-side preparation for expensive parsing, currency conversion, sessionization, attribution, and slowly changing dimensions.

Avoid:

- Ambiguous grains in one dataset.
- Large free-form SQL datasets when a governed mart or table can exist upstream.
- Dashboard-time joins that can change row counts in surprising ways.
- Duplicate metric logic split across charts.

## Joins And Multi-Dataset Work

- DataLens datasets can join source tables. If joined fields are not used in a chart, DataLens may optimize the source query by skipping some joins. That can improve speed but may return values that surprise authors who expected join filtering.
- SQL-query datasets run the custom SQL as a subquery whenever the source is accessed. Use this for flexible exploration, not as the default for heavy production dashboards.
- Multi-dataset charts process queries for each dataset independently. Use them only when the analytical relationship is clear.
- Selectors and charts from one dataset link automatically. Cross-dataset selector links need aliases, and the filter field must exist in the target chart's dataset.

## Calculated Fields

- Dataset-level calculated fields are reusable by all charts and dashboard selectors based on that dataset. Use them for canonical business metrics.
- Chart-level calculated fields are local to that chart. Use them for ad-hoc display logic, not shared KPI definitions.
- Avoid formula loops and expensive row-level transformations on large tables.
- Keep a metric catalog close to the dataset: name, formula, aggregation, grain assumptions, owner, and validation query.

## LOD Expressions

Use DataLens LOD keywords when aggregation must differ from the chart grouping:

- `FIXED`: aggregate by an explicit dimension list. Without dimensions, aggregate over one global group.
- `INCLUDE`: add dimensions to the chart grouping for a measure.
- `EXCLUDE`: remove dimensions from the chart grouping for a measure.

Rules of thumb:

- Use LOD for percent-of-total, contribution, cohort totals, and comparisons to parent groups.
- Check filter order. LOD and filtering interactions are easy to misread.
- Keep the top-level aggregation compatible with chart dimensions.
- Validate LOD measures against source SQL on sample slices before shipping.

## Parameters

- Dataset and chart parameters can feed formulas and change chart behavior.
- Dashboard parameters filter widgets when opening a dashboard or when used in calculated field formulas.
- Link parameters can override dashboard and selector defaults. Reserved keys include `tab`, `state`, `mode`, `focus`, `grid`, `scale`, `tz`, `timezone`, `date`, `datetime`, and `_action_params`.
- For parameterized QL charts, selectors with manual input can control query variables in `{{variable}}` format.

Use parameters for:

- What-if inputs.
- Dynamic aggregation level such as day/week/month.
- Switching scenarios or comparison baselines.
- Pre-filtered links from another dashboard, Wiki page, or operational system.

Do not use parameters as an undocumented replacement for governed dimensions.

## Selectors And Interactions

- Selectors filter linked widgets and can apply to one tab, selected tabs, or the entire dashboard.
- Selector values are synchronized and retained when switching tabs.
- Selector types include list, input field, calendar, checkbox, and JS selector.
- If no selector value is selected, DataLens returns all data for that field. On large sources, set safe defaults.
- Adding a selector for a field can override chart-level filters on that field. Use a duplicated field if true double filtering is needed.
- Selector groups may use Apply and Reset buttons. Use Apply when several selectors would otherwise trigger too many source queries.

## Chart-By-Chart Filtering

- A chart can act as a filter for other charts. Users filter linked charts by clicking a point, bar, pie segment, table row, map element, and similar supported marks.
- Supported wizard chart types include line, area, column, bar, scatter, pie, donut, table, pivot table, point map, choropleth map, and combined chart.
- Chart filtering uses dataset dimensions, except unsupported fields such as string trees, hierarchies, and markup fields. Chart-level fields do not participate.
- Table cell clicks filter by all dimensions in the selected row. Map clicks filter by dimensions used in the chart except coordinates.
- Filtered state is stored in the dashboard `state` URL parameter and can be shared.

## Dashboard Structure

- Dashboards are pages or sets of pages containing widgets. Tabs create additional pages.
- Put as few charts as practical on the active tab. DataLens runs source queries for every chart on that active tab.
- Use tabs by workflow: executive overview, diagnostics, operational detail, definitions/audit.
- Keep selector scope explicit: global, tab-level, or local.
- Pin only selectors or KPI context that must stay visible during scroll.
- Configure mobile/widget order instead of assuming desktop layout will collapse acceptably.

## Performance Plan

Source:

- Sort or cluster large source tables by frequent filters, usually dates and business partitions.
- Use explicit types and avoid text dates.
- Pre-aggregate or materialize high-cardinality, expensive, or billion-row use cases.
- In ClickHouse, align `ORDER BY` with common filtering paths, use partitioning sensibly, and consider `LowCardinality` for low-cardinality strings.
- Do not render excessive points. Aggregate or sample when the business question does not require raw granularity.

DataLens:

- Set selector defaults to avoid full-table opens.
- Reduce auto-update frequency; never refresh faster than source freshness.
- Enable "Load only visible charts" when lower-page widgets are expensive.
- Limit "Number of concurrently loaded widgets" when the source cannot handle bursty dashboard opens.
- Use loading priority so visible charts or selectors load in the intended order.
- Use caching of frequently requested source data where available and appropriate.

Target: important executive tabs should feel interactive in 2-3 seconds on warm/common paths. If this is impossible, say why and redesign the data path.

## Governance

- Use workbooks as portable containers for related objects and collections to organize departmental access.
- Workbook permissions apply to contained objects. Collection permissions apply to nested collections, workbooks, and objects.
- Use groups rather than individual users where possible.
- Dashboard versions are created on save and can be current, draft, or outdated. Drafts hide changes from normal viewers until promoted.
- Version history is limited and does not include all object changes: access changes, chart wizard changes, dataset settings, connection settings, and source data changes are outside dashboard version diffs.
- Keep a DataLens text/widget or linked documentation page with KPI definitions, owner, data freshness, caveats, and support path.

## Source Anchors

- DataLens optimization recommendations: https://yandex.cloud/en/docs/datalens/concepts/optimization_recommendations
- Dashboard settings: https://yandex.cloud/en/docs/datalens/dashboard/settings
- Dataset concepts: https://github.com/datalens-tech/docs/blob/main/en/datalens/dataset/index.md
- Data joining: https://yandex.cloud/en/docs/datalens/concepts/data-join
- Calculated fields: https://datalens.tech/docs/en/concepts/calculations/index.html
- LOD expressions: https://yandex.cloud/en/docs/datalens/concepts/lod-aggregation
- Selectors: https://yandex.cloud/en/docs/datalens/dashboard/selector
- Chart-by-chart filtering: https://yandex.cloud/en/docs/datalens/dashboard/chart-chart-filtration
- Dashboard parameters: https://yandex.cloud/en/docs/datalens/dashboard/dashboard_parameters
- Dashboard versioning: https://yandex.cloud/en/docs/datalens/dashboard/versioning
- Workbook operations and access: https://yandex.cloud/en/docs/datalens/workbooks-collections/workbooks-operations
