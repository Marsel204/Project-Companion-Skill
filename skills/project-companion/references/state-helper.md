# Offline project-state helper

`scripts/project_state.py` validates or transforms an already-loaded JSON snapshot. It never reads/writes Notion, saves local files, schedules work, or sends notifications. Its outputs are proposals until confirmed external writes occur. Use it for complex state changes and graph checks, not as a replacement for agent judgment.

Invoke `python` with the helper's absolute path and one command: `validate`, `next`, `apply`, `review`, or `checkin`. Supply a JSON request on standard input. Capture stdout as JSON; exit 0 means the operation is valid, exit 2 means a structured validation/conflict error. Secrets are never needed.

## Snapshot

Use [the complete fictional example](../assets/example-project.json) for the field shape. It is test/example data, not a real saved project. Map Notion properties into this normalized shape and preserve additional source metadata. An empty newly drafted project can have no focus/items; established tasks/actions follow milestone → task → action parent levels.

- `schema_version`: 1.
- `project`: `id`, `title`, `state`, `focus` (milestone ID or null), `spec`, `reminder`.
- `spec`: `goal`, nonempty `success_criteria`; optional scope, hard deadline, target dates, requirements, assumptions, and unknowns.
- `reminder`: `enabled`, `mode` (`review` or `monitor`), `timezone` (IANA name or null while disabled), confirmed `schedule_id` (or null), `cancellation_pending`.
- `items`: each has `id`, `project_id`, `parent`, `level`, `title`, `state`, nonempty `criteria`, optional `met_criteria`, `dependencies`, estimated `minutes`, `note`, and `evidence`.
- `history`: operation identity, payload fingerprint, original operation, and resolved item identity.
- `occurrences`: stable composite key and `reserved`, `delivered`, or `unknown` delivery state.

## Requests

All commands use `{"snapshot": ...}`.

| Command | Additional input | Output |
| --- | --- | --- |
| `validate` | None | Validity; checks hierarchy, identities, dependency cycles, state, criteria and timezone. |
| `next` | Optional positive `budget` in minutes | One ready `action` or null, a reason, and whether a ready action needs decomposition/estimation. |
| `review` | None | Current milestone and unmet criteria, completed milestone outcomes, blockers, explicitly labeled work-item counts. |
| `apply` | `operation` object | Updated proposal snapshot; duplicate flag or structured error with original snapshot. |
| `checkin` | Confirmed `schedule_id`, stable offset-bearing ISO `occurrence`, `phase`, optional `meaningful` | Updated occurrence proposal; whether to notify or reconcile. |

`next` filters blocked ancestors and dependencies and prefers the focus milestone/in-progress work. The agent still assesses deadlines and may choose a better unblocking action. It refuses to claim an action with an unknown estimate fits a supplied time budget.

## Operations

Every operation needs a stable `id` and `type`. Keep the same ID/payload on retry. A changed payload with that ID is a conflict. IDs and history in a working snapshot do not establish external uniqueness.

- `progress`, `complete`, `block`, `reopen`, `drop`: use `item_id`; optional `note`, `evidence`, and `expected` field/value comparisons. A completion without `item_id` resolves only one uniquely ready action; ambiguous targets fail without mutation.
- Complete an action from a clear user report. Complete a task/milestone only with its `met_criteria` fully supplied. Parents are never auto-completed.
- `revise_spec`: provide `changes`, `accepted: true`, and a reason. This flag represents actual user acceptance; the agent must not manufacture it. Unchanged fields, including deadlines, are preserved.
- `set_project_state`: provide `state`; project completion additionally requires `confirmed: true` from actual user confirmation and `met_success_criteria`. Pause/complete/abandon disables proposed reminders and marks scheduler cancellation pending; it does not cancel the actual schedule.

`checkin` phases: `reserve`, `delivered`, `unknown`. Reservation grants permission to compose a check-in only after the reservation is durably saved under the integration's verified semantics. Repeated reserved/unknown occurrences need reconciliation; delivered occurrences are suppressed. A transition to delivered needs host evidence. See [delivery limitations](check-ins.md).
