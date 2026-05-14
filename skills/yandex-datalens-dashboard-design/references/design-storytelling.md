# Design And Storytelling

## Start With The Decision

Before layout or chart choice, write:

- Who uses the dashboard.
- What decision or operational action it supports.
- How often the user opens it.
- What "good", "bad", and "needs attention" mean.
- What comparison makes the metric meaningful: plan, previous period, cohort, peer group, target, or control.
- What the user should do after seeing an anomaly.

If the dashboard cannot name a decision, it is probably an exploratory workbook, not a production dashboard.

## Narrative Structure

Use a layered dashboard story:

1. **Executive status**: core KPIs, target deltas, alerts, freshness, and scope.
2. **Diagnostics**: the few charts that explain why KPI movement happened.
3. **Segmentation**: product, channel, region, cohort, customer type, or funnel step.
4. **Operational detail**: tables and drill-down views for investigation.
5. **Definitions**: metric logic, owners, caveats, and support path.

Each tab should answer one question. Good tab names are questions or workflows, not generic nouns.

## Layout

- Put the highest-value answer in the upper-left/upper area. Users scan from status to explanation.
- Align charts to a strict grid and keep related controls close to the charts they affect.
- Do not exceed six major analytical widgets on one tab unless the tab is explicitly operational and dense.
- Use repeated layout patterns across tabs: KPI row, diagnostic charts, detail table.
- Keep whitespace functional. It should group and separate, not decorate.
- Use "bento" grouping only when it clarifies sections. Do not turn every widget into a decorative card.
- Avoid glassmorphism, gradients, shadows, and transparency when they reduce contrast or make charts harder to read.

## Chart Choice

- **Indicator/KPI**: current value, target, delta, and status.
- **Line chart**: trend over continuous time.
- **Column/bar chart**: category comparison and ranking. Prefer horizontal bars for long labels.
- **Stacked bar/area**: part-to-whole over categories or time only when totals and composition both matter.
- **Table/pivot**: lookup, audit, exact values, and operational detail.
- **Scatter**: relationship between two measures, with color/size only for meaningful dimensions.
- **Map**: spatial question. Do not use maps for category lists just because regions exist.
- **Pie/donut**: use rarely, only for a few stable parts of a whole. Bars are usually easier to compare.
- **Combined chart**: only when units and axes are clear. Do not hide two unrelated stories in one canvas.

Reject chart types that make the comparison harder than the underlying table.

## Color

- Assign semantic colors and keep them stable across tabs.
- Use neutral colors for context and one accent for the current message.
- Reserve red/green for status when the business semantics really are bad/good.
- Do not encode two meanings with the same color on the same page.
- Keep enough contrast for labels, axes, selectors, and map layers.
- Avoid rainbow palettes for ordered values. Use sequential or diverging palettes that match the meaning.

## Text And Labels

- Titles should state the insight or question, not merely the chart type.
- Subtitles should carry scope: period, filter, unit, and denominator.
- Use direct labels when they reduce lookup. Remove redundant legends, axes, or labels when the chart remains clear.
- Put units in field names or axis titles. Do not force users to infer thousands, millions, percent, or currency.
- Use annotations for abnormal events: launches, outages, pricing changes, campaigns, data incidents.
- Avoid long prose blocks inside production dashboards. Link to definitions if detail is needed.

## Interaction

- Use selectors for high-value slicing, not every available dimension.
- Prefer a short selector row: date, key segment, geography/product, and maybe one scenario parameter.
- Use tab-level selectors when a control is meaningful only for that page.
- Use chart filtering for guided drill-down when users naturally click a segment to investigate.
- Provide Reset/Apply in selector groups when multiple selectors would cause repeated query bursts.
- Keep interactions discoverable through layout and labels. Do not rely on hidden tricks.

## Data Storytelling Patterns

- **Metric tree**: revenue -> orders x AOV -> conversion x traffic x basket.
- **Funnel**: stage conversion, loss points, and segment comparison.
- **Cohort**: retention, repeat usage, payback, or activation by cohort start.
- **Variance bridge**: actual vs plan explained by volume, mix, price, conversion, and cost drivers.
- **Anomaly brief**: what moved, how much, where, since when, likely cause, owner action.
- **Executive pulse**: status, top drivers, risks, and next review date.

Use the narrative pattern that matches the business question. Do not paste a generic KPI grid over every domain.

## Accessibility And Robustness

- Make charts readable without relying only on color.
- Check long labels, Cyrillic labels, empty states, null values, zero denominators, and mobile layout.
- Show data freshness and source caveats where users make decisions.
- Use safe empty states: "No data for selected filters" is better than a blank chart.
- Validate that filters do not silently change denominator logic.

## Anti-Patterns

- Dashboard as a chart dump.
- KPI tiles without targets or comparison.
- Too many global selectors.
- Mixed grains on one page without warning.
- Different colors for the same metric across tabs.
- Dual axes with unrelated units.
- Pie charts with many slices.
- Tables used as dashboards because metric definitions were not agreed.
- "Modern" visual styling that lowers legibility.

## Useful External Anchors

- DataLens dashboard concepts: https://yandex.cloud/en/docs/datalens/concepts/dashboard
- DataLens widgets: https://yandex.cloud/en/docs/datalens/dashboard/widget
- Storytelling with Data concepts: understand context, remove clutter, focus attention, and use text intentionally.
- Stephen Few dashboard design concepts: dashboard pages should support rapid monitoring with clear, compact, high-signal displays.
