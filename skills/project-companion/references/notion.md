# Notion record and synchronization

## Setup and capability check

Use a supported writable Notion integration exposed by the host. Discover actual tool names; do not fabricate calls or assume search implies write access. Verify page-body reads, work-item queries with pagination, item creation/update, activity writes, stable IDs/URLs, and edit metadata. Confirm the designated project page/data source and standing authorization for routine project updates.

Provision only within the selected project when authorized. If database/schema creation is unavailable, provide the concrete template for the user to duplicate or configure. If Notion is unavailable, label chat content as unsaved. Never request that the user paste a token into chat; use the host's credential flow. A new API adapter requires explicit scope rather than silently adding a service.

## Minimal mapping

Keep a project page, work-items database, and append-only activity/operation log. Put lengthy text in page bodies. Map logical fields to existing compatible properties; record the mapping on the project page rather than assuming exact property names.

| Record | Required logical fields |
| --- | --- |
| Project | Stable ID/URL, title, state, living spec, focus-milestone link, timezone, reminder policy, last successful review. |
| Work item | ID, project link, parent link, level, title, state, completion criteria, dependencies; optional time estimate, date/type, note, evidence. |
| Activity/operation | Operation ID, timestamp with offset, intended change, old/new values, affected item IDs, confirmed steps, source, status (pending/saved/uncertain). |
| Schedule binding | Project ID, schedule ID, enabled state, cadence/timezone, cancellation-pending status, stable occurrence records and observed delivery state. |

Milestones belong directly to the project; tasks belong to milestones; actions belong to tasks. A project's parent and dependency references must not point into another project. Work-item states are planned, ready, in progress, blocked, done, and dropped. Partial progress stays in progress. Project states are draft, active, paused, complete, and abandoned.

## Read and save

1. Load the project body, property mapping, relevant items, and pending operations. Follow pagination until the scope needed for a complete review is available. Otherwise label the review as partial.
2. Refresh affected fields before a write. Prepare a field-specific update against their observed values; retain unrelated fields and manual notes.
3. Assign one stable operation ID and record its intent before a multi-record mutation. Query this ID when resuming after an uncertain result. Local recovery files are temporary aids; Notion remains authoritative.
4. Apply authorized changes through actual tools. Record confirmed item IDs and each successful step. After a save, read back the relevant fields or use an unambiguous confirmed tool result. Mark the operation saved only when all necessary writes and log steps are confirmed.
5. Report the useful result; identify any unsaved or uncertain changes plainly. A helper-generated snapshot is still a proposal until confirmed Notion writes have occurred.

Same-field changes produce a conflict question; unrelated edits can be merged. Without atomic conditional writes, refreshes reduce risk but cannot guarantee race-free updates. Process companion writes sequentially; if overlapping operations are detected, reconcile them instead of continuing blind writes.

## Failure recovery

On timeout after creation, search by stable logical/operation identity and recover the returned item before retrying creation. On partial updates, compare intended changes with current fields and retry only missing steps, checking for intervening edits. Repeated IDs with different intents are conflicts.

Honor provider rate-limit timing with at most three attempts per interaction. Stop persistent failures and keep useful unsaved proposals visible. Lost access, deleted references, or incomplete queries must not appear as saved progress.

No API uniqueness or transaction guarantee is assumed. Sequential reconciliation is supported; concurrent create races remain a live-integration limitation until the chosen tools establish a stronger guarantee.

Current API behavior and required update permissions: [Notion update-page documentation](https://developers.notion.com/reference/patch-page).
