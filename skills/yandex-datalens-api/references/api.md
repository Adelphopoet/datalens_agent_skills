# DataLens Public API Index

Source: `references/openapi.json` from `https://api.datalens.tech/json/`.
Generated: `2026-05-14T07:30:49+00:00`.
OpenAPI SHA256: `a3187df8d708cda2164036c7ef5183e5be81fd8b59ff28466edd3cfc15efb885`.

All methods are `POST /rpc/<method>` and require `x-yacloud-subjecttoken`, `x-dl-org-id`, `x-dl-api-version: 1`, and `Content-Type: application/json`. The CLI can also send `Authorization: Bearer <TOKEN>` when `--auth-header Authorization` is used.

Use `scripts/datalens_cli.py example <method>` for full request skeletons. The table below shows top-level required fields, variant-specific bodies, extra headers, and compact body skeletons when they fit.

Total RPC methods: 79.

## Audit

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `getAuditEntriesUpdates` | Get updated entries for audit | `from` | - | `{"from":"<string>"}` | `GetAuditEntriesUpdatesArgs` | `GetAuditEntriesUpdatesResult` |
| `getAuditEntryPermissionsForUser` | Get entry permissions for user | `entryIds, userId` | - | `{"entryIds":[],"userId":"<string>"}` | `GetAuditEntryPermissionsForUserArgs` | `GetAuditEntryPermissionsForUserResult` |

## Collection

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createCollection` | Create collection | `title, parentId` | - | `{"title":"<string>","parentId":"<string>"}` | `CreateCollectionArgs` | `CreateCollectionResult` |
| `deleteCollection` | Delete collection | `collectionId` | - | `{"collectionId":"<string>"}` | `DeleteCollectionArgs` | `DeleteCollectionResult` |
| `deleteCollections` | Delete collections | `collectionIds` | - | `{"collectionIds":[]}` | `DeleteCollectionsArgs` | `DeleteCollectionsResult` |
| `getCollection` | Get collection | `collectionId` | - | `{"collectionId":"<string>"}` | `GetCollectionArgs` | `GetCollectionResult` |
| `getCollectionBreadcrumbs` | Get collection breadcrumbs | `collectionId` | - | `{"collectionId":"<string>"}` | `GetCollectionBreadcrumbsArgs` | `GetCollectionBreadcrumbsResult` |
| `getCollectionContent` | Get collection content | `collectionId` | - | `{"collectionId":"<string>"}` | `GetStructureItemsArgs` | `GetStructureItemsResult` |
| `getCollectionsByIds` | Get collections list by ids | `collectionIds` | - | `{"collectionIds":[]}` | `GetCollectionsByIdsArgs` | - |
| `getRootCollectionPermissions` | Get root collection permissions | - | - | `{}` | - | `GetRootCollectionPermissionsResult` |
| `listCollectionAccessBindings` | List collection access bindings | `collectionId` | - | `{"collectionId":"<string>"}` | `ListCollectionAccessBindingsArgs` | `ListIamAccessBindingsResult` |
| `moveCollection` | Move collection | `collectionId, parentId` | - | `{"collectionId":"<string>","parentId":"<string>"}` | `MoveCollectionArgs` | `Collection` |
| `moveCollections` | Move collections | `collectionIds, parentId` | - | `{"collectionIds":[],"parentId":"<string>"}` | `MoveCollectionsArgs` | - |
| `updateCollection` | Update collection | `collectionId` | - | `{"collectionId":"<string>"}` | `UpdateCollectionArgs` | `Collection` |
| `updateCollectionAccessBindings` | Update collection access bindings | `collectionId, deltas` | - | `{"collectionId":"<string>","deltas":[]}` | `UpdateCollectionAccessBindingsArgs` | `DatalensOperation` |

## Connection

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createConnection` | Create connection | `variant-specific` | - | `{"counter_id":"<string>","dir_path":"<string>","name":"<string>","token":"<string>"}` | `ConnectionCreate` | `CreateConnectionResult` |
| `deleteConnection` | Delete connection | `connectionId` | - | `{"connectionId":"<string>"}` | - | - |
| `getConnection` | Get connection | `connectionId` | `x-dl-audit-mode` | `{"connectionId":"<string>"}` | - | `ConnectionRead` |
| `updateConnection` | Update connection | `connectionId` | - | `{"connectionId":"<string>"}` | - | - |

## Dashboard

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createDashboard` | [Experimental] Create dashboard | `entry` | - | `run datalens_cli.py example createDashboard` | `CreateDashboardV1Args` | - |
| `deleteDashboard` | Delete dashboard | `dashboardId` | - | `{"dashboardId":"<string>"}` | `DeleteDashboardArgs` | - |
| `getDashboard` | [Experimental] Get dashboard | `dashboardId` | `x-dl-audit-mode` | `{"dashboardId":"<string>"}` | `GetDashboardV1Args` | `GetDashboardV1Result` |
| `updateDashboard` | [Experimental] Update dashboard | `entry, mode` | - | `run datalens_cli.py example updateDashboard` | `UpdateDashboardV1Args` | - |

## Dataset

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createDataset` | Create dataset | `dataset` | - | `{"dataset":{}}` | `DatasetCreate` | `DatasetRead` |
| `deleteDataset` | Delete dataset | `datasetId` | - | `{"datasetId":"<string>"}` | - | - |
| `getDataset` | Get dataset | `datasetId` | `x-dl-audit-mode` | `{"datasetId":"<string>"}` | - | `DatasetRead` |
| `updateDataset` | Update dataset | `datasetId` | - | `{"datasetId":"<string>"}` | - | `DatasetRead` |
| `validateDataset` | Validate dataset | `datasetId` | - | `{"datasetId":"<string>"}` | - | `DatasetRead` |

## Editor

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createEditorChart` | [Experimental] Create editor chart | `entry` | - | `run datalens_cli.py example createEditorChart` | `CreateEditorChartArgs` | `CreateEditorChartResult` |
| | Description: Creates the specified Editor chart. | | | | | |
| `deleteEditorChart` | Delete editor chart | `chartId` | - | `{"chartId":"<string>"}` | `DeleteEditorChartArgs` | - |
| | Description: Deletes the specified Editor chart. | | | | | |
| `getEditorChart` | [Experimental] Get editor chart | `chartId` | `x-dl-audit-mode` | `{"chartId":"<string>"}` | `GetEditorChartArgs` | `GetEditorChartResult` |
| | Description: Returns the specified Editor chart. | | | | | |
| `updateEditorChart` | [Experimental] Update editor chart | `mode, entry` | - | `run datalens_cli.py example updateEditorChart` | `UpdateEditorChartArgs` | `UpdateEditorChartResult` |
| | Description: Updates the specified Editor chart. | | | | | |

## EmbeddingSecrets

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createEmbeddingSecret` | Create embedding secret | `title, workbookId` | - | `{"title":"<string>","workbookId":"<string>"}` | `CreateEmbeddingSecretArgs` | `CreateEmbeddingSecretResult` |
| | Description: Creates the key for embedding. | | | | | |
| `deleteEmbeddingSecret` | Delete embedding secret | `embeddingSecretId` | - | `{"embeddingSecretId":"<string>"}` | `DeleteEmbeddingSecretArgs` | `DeleteEmbeddingSecretResult` |
| | Description: Deletes the specified key for embedding. | | | | | |
| `getEmbeddingSecret` | Get embedding secret | `embeddingSecretId` | - | `{"embeddingSecretId":"<string>"}` | `GetEmbeddingSecretArgs` | `EmbeddingSecret` |
| | Description: Returns the specified key for embedding. | | | | | |
| `listEmbeddingSecrets` | List embedding secrets | `workbookId` | - | `{"workbookId":"<string>"}` | `ListEmbeddingSecretsArgs` | - |
| | Description: Lists keys for embedding of the specified workbook. | | | | | |

## Embeds

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createEmbed` | Create embed | `title, embeddingSecretId, entryId, depsIds, unsignedParams, privateParams, publicParamsMode, settings` | - | `run datalens_cli.py example createEmbed` | `CreateEmbedArgs` | `Embed` |
| | Description: Creates the specified embedding. | | | | | |
| `deleteEmbed` | Delete embed | `embedId` | - | `{"embedId":"<string>"}` | `DeleteEmbedArgs` | `DeleteEmbedResult` |
| | Description: Deletes the specified embedding. | | | | | |
| `listEmbeds` | List embeds | `entryId` | - | `{"entryId":"<string>"}` | `ListEmbedsArgs` | - |
| | Description: Lists embeddings of the specified entry. | | | | | |
| `updateEmbed` | Update embed | `embedId, title, embeddingSecretId, depsIds, unsignedParams, privateParams, publicParamsMode, settings` | - | `run datalens_cli.py example updateEmbed` | `UpdateEmbedArgs` | `Embed` |
| | Description: Updates the specified embedding. | | | | | |

## Entries

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `getEntriesPermissions` | Get entries permissions | `entryIds` | - | `{"entryIds":[]}` | `GetEntriesPermissionsArgs` | `GetEntriesPermissionsResult` |
| `getEntriesRelations` | Get entries relations | `entryIds` | - | `{"entryIds":[]}` | `GetEntriesRelationsArgs` | `GetEntriesRelationsResult` |
| | Description: Returns the specified DataLens entries relations. | | | | | |

## Folder

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createFolder` | CreateFolder | `key` | - | `{"key":"<string>"}` | `CreateFolderArgs` | `CreateFolderResult` |

## Licensing

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `assignLicenses` | Assign licenses | `userIds` | - | `{"userIds":[]}` | `AssignLicensesArgs` | - |
| `getLicenses` | Get licenses | - | - | `{}` | `GetLicensesArgs` | `GetLicensesResult` |
| `getLicensesLimit` | Get licenses limit | - | - | `{}` | - | `LicenseLimits` |
| `setLicenseLimit` | Set licenses limit | `value` | - | `{"value":0}` | `SetLicenseLimitArgs` | `LicenseLimits` |

## Navigation

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `getEntries` | Get entries | - | - | `{}` | `GetEntriesArgs` | `GetEntriesResult` |
| `listDirectory` | List directory | - | - | `{}` | `ListDirectoryArgs` | `ListDirectoryResult` |
| | Description: Lists entries from the specified directory. | | | | | |

## QL

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createQLChart` | [Experimental] Create QL chart | `data, template` | - | `{"template":"ql","data":{}}` | `CreateQLChartArgs` | - |
| `deleteQLChart` | Delete QL chart | `chartId` | - | `{"chartId":"<string>"}` | `DeleteQLChartArgs` | - |
| `getQLChart` | [Experimental] Get QL chart | `chartId` | `x-dl-audit-mode` | `{"chartId":"<string>"}` | `GetQLChartArgs` | - |
| | Description: Returns the specified QL chart. | | | | | |
| `updateQLChart` | [Experimental] Update QL chart | `entryId, template, mode, data` | - | `{"entryId":"<string>","template":"ql","mode":"save","data":{}}` | `UpdateQLChartArgs` | - |

## Reports

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createReport` | [Experimental] Create report | `data, meta` | - | `run datalens_cli.py example createReport` | `CreateReportV1Args` | `CreateReportV1Result` |
| `deleteReport` | Delete report | `entryId` | - | `{"entryId":"<string>"}` | `DeleteReportArgs` | - |
| `getReport` | [Experimental] Get report | `entryId` | `x-dl-audit-mode` | `{"entryId":"<string>"}` | `GetReportV1Args` | `GetReportV1Result` |
| `updateReport` | [Experimental] Update report | `entryId, data, mode, meta` | - | `run datalens_cli.py example updateReport` | `UpdateReportV1Args` | `UpdateReportV1Result` |

## Wizard

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createWizardChart` | [Experimental] Create wizard chart | `data, template` | - | `{"template":"datalens","data":{}}` | `CreateWizardChartArgs` | - |
| `deleteWizardChart` | Delete wizard chart | `chartId` | - | `{"chartId":"<string>"}` | `DeleteWizardChartArgs` | - |
| `getWizardChart` | [Experimental] Get wizard chart | `chartId` | `x-dl-audit-mode` | `{"chartId":"<string>"}` | `GetWizardChartArgs` | - |
| `updateWizardChart` | [Experimental] Update wizard chart | `entryId, template, mode, data` | - | `{"entryId":"<string>","template":"datalens","mode":"save","data":{}}` | `UpdateWizardChartArgs` | - |

## Workbook

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `createWorkbook` | Create workbook | `title` | - | `{"title":"<string>"}` | `CreateWorkbookArgs` | `CreateWorkbookResult` |
| `deleteWorkbook` | Delete workbook | `workbookId` | - | `{"workbookId":"<string>"}` | `DeleteWorkbookArgs` | `Workbook` |
| `deleteWorkbooks` | Delete workbooks | `workbookIds` | - | `{"workbookIds":[]}` | `DeleteWorkbooksArgs` | - |
| `getWorkbook` | Get workbook | `workbookId` | - | `{"workbookId":"<string>"}` | `GetWorkbookArgs` | `GetWorkbookResult` |
| `getWorkbookEntries` | Get workbook entries | `workbookId` | - | `{"workbookId":"<string>"}` | `GetWorkbookEntriesArgs` | `GetWorkbookEntriesResult` |
| `getWorkbooksByIds` | Get workbook list by ids | `workbookIds` | - | `{"workbookIds":[]}` | `GetWorkbooksByIdsArgs` | - |
| `getWorkbooksList` | Get workbooks list | - | - | `{}` | `GetWorkbooksListArgs` | `GetWorkbooksListResult` |
| `listWorkbookAccessBindings` | List workbook access bindings | `workbookId` | - | `{"workbookId":"<string>"}` | `ListWorkbookAccessBindingsArgs` | `ListIamAccessBindingsResult` |
| `moveWorkbook` | Move workbook | `workbookId, collectionId` | - | `{"workbookId":"<string>","collectionId":"<string>"}` | `MoveWorkbookArgs` | `Workbook` |
| `moveWorkbooks` | Move workbooks | `workbookIds, collectionId` | - | `{"workbookIds":[],"collectionId":"<string>"}` | `MoveWorkbooksArgs` | - |
| `updateWorkbook` | Update workbook | `workbookId` | - | `{"workbookId":"<string>"}` | `UpdateWorkbookArgs` | `Workbook` |
| `updateWorkbookAccessBindings` | Update workbook access bindings | `workbookId, deltas` | - | `{"workbookId":"<string>","deltas":[]}` | `UpdateWorkbookAccessBindingsArgs` | `DatalensOperation` |

## WorkbookExport

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `cancelWorkbookExport` | Cancel workbook export | `exportId` | - | `{"exportId":"<string>"}` | `CancelWorkbookExportArgs` | `CancelWorkbookExportResult` |
| `getWorkbookExportResult` | Get workbook export result | `exportId` | - | `{"exportId":"<string>"}` | `GetWorkbookExportResultArgs` | `GetWorkbookExportResultResult` |
| `getWorkbookExportStatus` | Get workbook export status | `exportId` | - | `{"exportId":"<string>"}` | `GetWorkbookExportStatusArgs` | `GetWorkbookExportStatusResult` |
| `startWorkbookExport` | Start workbook export | `workbookId` | - | `{"workbookId":"<string>"}` | `StartWorkbookExportArgs` | `StartWorkbookExportResult` |

## WorkbookImport

| Method | Summary | Required fields | Extra headers | Body skeleton | Request schema | Response schema |
| --- | --- | --- | --- | --- | --- | --- |
| `getWorkbookImportStatus` | Get workbook import status | `importId` | - | `{"importId":"<string>"}` | `GetWorkbookImportStatusArgs` | `GetWorkbookImportStatusResult` |
| `startWorkbookImport` | Start workbook import | `data, title, collectionId` | - | `{"data":{},"title":"<string>","collectionId":"<string>"}` | `StartWorkbookImportArgs` | `StartWorkbookImportResult` |
