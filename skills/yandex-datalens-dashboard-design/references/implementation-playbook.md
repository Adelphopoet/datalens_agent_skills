# Implementation Playbook

Use this playbook when the user wants an agent to create or update a Yandex DataLens dashboard, not just design one. It connects the dashboard design skill to the API automation skill.

The design skill owns the analytical decisions. The API skill owns authentication, schema inspection, RPC calls, and response handling. Do not skip the design contract and jump straight to payloads unless the user explicitly asks for a low-fidelity API smoke test.

## Required Inputs

Collect or discover these before mutating DataLens:

- Business goal, audience, cadence, and the action the dashboard should support.
- Metric contract: formulas, grain, filters, units, owner, freshness, caveats, and validation queries.
- Source details: existing workbook, collection, connection, dataset, or enough information to create them.
- Field map: source column names, business field names, dimensions, measures, date fields, and selector fields.
- Target object names: workbook, dataset, charts, dashboard, and optional collection.
- Permissions: viewer/editor/admin groups or an explicit decision to leave access unchanged.
- Deployment mode: draft only, publish after validation, or update an existing dashboard.

If credentials, org id, or a target workbook/collection are missing, stop before API mutation and ask for the missing operational input. Never ask for secrets in chat if the environment variables can be set locally instead.

## Design To API Mapping

Translate the design output into API objects in this order:

| Design artifact | DataLens object | Main RPC methods |
| --- | --- | --- |
| Ownership and container | Workbook or collection | `createWorkbook`, `moveWorkbook`, `createCollection` |
| Source access | Connection | `getConnection`, `createConnection`, `updateConnection` |
| Semantic layer | Dataset | `createDataset`, `updateDataset`, `validateDataset` |
| Visual widgets | Wizard, QL, or editor charts | `createWizardChart`, `createQLChart`, `createEditorChart` |
| Page layout and interactions | Dashboard | `createDashboard`, `updateDashboard` |
| Sharing model | Access bindings | `updateWorkbookAccessBindings`, `updateCollectionAccessBindings` |

Prefer reusing existing connections and datasets when the user already has governed assets. Create new objects only when the requested dashboard needs a new semantic layer or isolated ownership.

## Build Sequence

1. Read the API method index and inspect exact schemas before building payloads:

   ```bash
   cd skills/yandex-datalens-api
   uv run scripts/datalens_cli.py methods --tag Workbook
   uv run scripts/datalens_cli.py methods --tag Dataset
   uv run scripts/datalens_cli.py methods --tag Dashboard
   uv run scripts/datalens_cli.py schema createDashboard --request
   ```

2. Confirm authentication is available:

   ```bash
   export DATALENS_ORG_ID="..."
   export DATALENS_IAM_TOKEN="..."
   uv run scripts/datalens_cli.py rpc getWorkbooksList --body '{}'
   ```

3. Create or select the container:

   ```json
   {
     "title": "Revenue Operations",
     "description": "Operational revenue dashboard"
   }
   ```

   Call `createWorkbook` only if there is no existing workbook. Store the returned `workbookId`.

4. Create or select the data foundation.

   For existing governed datasets, call `getDataset` and verify fields, grain, and permissions. For a new dataset, inspect `createDataset` and build the payload from the source-specific schema:

   ```bash
   uv run scripts/datalens_cli.py schema createDataset --request
   uv run scripts/datalens_cli.py example createDataset --include-optional
   ```

   Always validate new or changed datasets with `validateDataset` before creating charts.

5. Create charts from the chart plan.

   Use Wizard charts for standard DataLens visuals when possible. Use QL charts when the chart must own a parameterized query. Use editor charts only when the dashboard requires custom code.

   Minimal Wizard chart envelope:

   ```json
   {
     "template": "datalens",
     "workbookId": "<workbook-id>",
     "name": "Revenue trend",
     "data": {}
   }
   ```

   The `data` body is intentionally schema-light in the Public API. Build it by inspecting an existing chart with `getWizardChart` when possible, or create one small chart first and verify it in DataLens before generating the rest.

6. Create the dashboard layout.

   The bundled OpenAPI defines `createDashboard` with an `entry` object. `updateDashboard` additionally requires `mode`.

   Minimal dashboard envelope:

   ```json
   {
     "entry": {
       "workbookId": "<workbook-id>",
       "name": "Revenue dashboard",
       "data": {
         "counter": 1,
         "salt": "<stable-random-string>",
         "schemeVersion": 8,
         "tabs": [
           {
             "id": "tab-overview",
             "title": "Overview",
             "items": [],
             "layout": [],
             "connections": [],
             "aliases": {}
           }
         ],
         "settings": {
           "autoupdateInterval": null,
           "maxConcurrentRequests": 4,
           "silentLoading": false,
           "dependentSelectors": false,
           "expandTOC": false,
           "loadPriority": "charts",
           "hideTabs": false
         }
       },
       "meta": {}
     }
   }
   ```

   Each dashboard widget needs a matching item and layout entry. Keep ids stable so updates can be diffed and reviewed.

7. Apply access bindings only after the dashboard content is validated.

   Inspect the binding schema first:

   ```bash
   uv run scripts/datalens_cli.py schema updateWorkbookAccessBindings --request
   ```

   Prefer group subjects over individual users. Do not loosen collection-level access unless the user explicitly requested it.

## Dashboard Payload Rules

- Set `schemeVersion` to `8` unless the API schema changes.
- Use stable ids for tabs, widgets, controls, and layout entries.
- Keep `counter` greater than zero and increment it on structural updates.
- Put selectors near the widgets they affect, and reflect selector scope in dashboard `connections` and aliases.
- Use `maxConcurrentRequests`, `loadPriority`, and visible-chart loading decisions from the performance plan.
- Use a text or title widget for definitions only when it helps the viewer make a decision. Long documentation belongs outside the dashboard.
- Keep draft updates separate from publish updates. For `updateDashboard`, choose `mode: "save"` until validation passes.

## Agent Confirmation Gates

Stop and ask for confirmation before:

- Creating or updating connections, because secrets and source permissions are involved.
- Publishing or overwriting an existing production dashboard.
- Broadening workbook or collection permissions.
- Creating many charts or widgets after the first chart/dashboard smoke test has not been verified.
- Using Experimental chart/dashboard methods for a business-critical dashboard without a fallback plan.

## Validation Checklist

After API creation, verify:

- `getWorkbookEntries` shows the expected dataset, charts, and dashboard.
- `getDataset` or `validateDataset` returns the expected fields and no validation errors.
- `getDashboard` returns all tabs, items, layout entries, aliases, and settings.
- The first dashboard tab opens within the target latency budget.
- Selectors filter only the intended widgets.
- Metric values match the source validation query for at least one known slice.
- Access bindings match the requested group model.

If UI verification is possible, open the DataLens dashboard and inspect it visually. If UI verification is not possible, report that the API objects were created but visual layout and chart rendering still need browser validation.

## Failure Handling

- On a 4xx response, keep the redacted error body and request id. Inspect the method schema before retrying.
- On schema uncertainty for charts, create or inspect a single representative chart before bulk creation.
- On slow dashboards, fix source shape, selector defaults, and widget count before adding more layout polish.
- On permission errors, check workbook and collection bindings before changing object payloads.
- On Experimental API breakage, fall back to workbook import/export or manual UI handoff rather than guessing private fields.
