# Project companion implementation plan

Status: Planning deliverable; implementation has not started.
Date: 14 October 2026
Basis: [Project companion specification v0.1](project-companion-spec.md).

## Goal and scope

Deliver a usable project-companion skill that helps one person clarify a project, follow a hierarchy of meaningful steps, record progress in Notion, and receive agreed AI check-ins. A successful first version supports the complete loop: describe a goal → choose a small action → report progress → resume later → receive a useful check-in.

Use Codex as the proposed initial host and keep the workflow portable. This is a planning assumption, not a recorded user selection. If a different host is chosen, revise the adapter and scheduler milestones; the core workflow and Notion model stay applicable.

The user selected Notion and scheduled AI check-ins, with Google Calendar deferred. Preserve that scope. A dedicated app, separate notification service, autonomous project execution, and collaboration features are outside this plan.

## Current state and constraints

- The workspace contains the specification, with no existing application implementation or usable Git repository.
- No AEK enrollment exists in the workspace or its ancestors. Use a proportional workflow; no AEK freeze or GitHub approval procedure applies.
- A Codex automation-management tool is exposed. No Notion tool is currently callable. A tool's presence does not establish account access or full scheduler behavior.
- The specification is a review draft. Carry its acceptance scenarios A01–A19 into implementation verification; do not treat this plan as approval of an implementation or a protected test harness.
- This planning turn creates only this document. Credential configuration, Notion changes, skill installation, and schedule activation belong to a later implementation/setup request.

## Proposed components and artifacts

Stage the future skill package in the active workspace before installing it. The layout below is proposed, not created by this plan.

| Component | Proposed artifact | Responsibility |
| --- | --- | --- |
| Main skill | `project-companion/SKILL.md` | Trigger conditions, conversational workflow, context loading, and concise user-facing responses. |
| Core workflow | `references/workflow.md` | Intake, next-action selection, progress, replanning, and project completion rules. |
| Notion mapping | `references/notion.md` | Template/schema mapping, stable identities, reads/writes, pagination, and recovery. |
| Host adapter | `references/codex.md` | Actual tool names, schedule lifecycle, notification behavior, and host limits. |
| Project template | `templates/project.md` and schema notes | Living spec, work-item fields, and activity log structure. |
| Evaluation cases | `evals/` | Requirement-focused conversations and integration failure scenarios. |
| Supporting code, if needed | Small adapter/helper | Deterministic validation, mutation reconciliation, or a capability missing from supported tools. Create only where tools plus instructions cannot satisfy a requirement. |

Keep credentials in the host/connector. Notion remains the authoritative project record. Local fixtures and caches serve evaluation or recovery and do not replace live project state.

## Milestone sequence

| Milestone | Result | Depends on |
| --- | --- | --- |
| M0 | Integration feasibility and initial-host decision | Existing specification |
| M1 | Conversational skill and example project flow | Specification; final host is not needed for the portable draft |
| M2 | Minimal Notion template and reliable persistence | M0 |
| M3 | Complete progress, resume, and replanning loop | M1, M2 |
| M4 | Scheduled check-ins and lifecycle controls | M0, M3 |
| M5 | Verified package and pilot setup instructions | M1–M4 |
| M6 | Two-week real-project pilot and improvement decision | M5 and user opting into pilot setup |

M1 can be drafted while M0 capabilities are being resolved. Execution remains sequential unless the user requests parallel agents. Do not add installation, publishing, or a separate service simply to keep a milestone moving.

### M0 — Validate integration feasibility

Inspect the selected host's current supported integrations and identify how the companion can read and update the designated Notion project. Record the exact capabilities, account prerequisites, workspace access, and template-provisioning approach.

Check Notion access for page-body reads, paginated work-item queries, item creation/update, activity entries, stable IDs/URLs, and edit metadata. Decide whether an existing writable integration is sufficient; if not, describe the smallest scoped adapter and its setup requirements before expanding implementation scope.

Check scheduling for create/view/update/pause/cancel, stable schedule identity, occurrence identity, timezone behavior, unattended tool availability, actual notification delivery, and recovery after the host is unavailable. Prefer a chat-attached schedule for this ongoing companion when supported. Inspect scheduler failures without activating a real recurring reminder during planning.

**Exit criteria:** a capability matrix identifies supported, unsupported, and unverified operations; an integration path exists for M2 and M4; the initial-host assumption is resolved before writing its adapter. Unsupported requirements remain visibly unresolved.

**Important feasibility decision:** A13 asks for no duplicate notifications after retries. Recording an occurrence before notification can lose a notification after a crash; recording it afterward can permit duplicates. Read-before-write checks alone also cannot guarantee uniqueness under concurrent execution. Establish what the host guarantees. If it cannot provide the necessary delivery/occurrence controls, propose a precise change to A13 for user review rather than claiming a guarantee or introducing an unrequested persistent service. The unchanged specification cannot be declared satisfied in that case.

**Verification:** capability inspection and, once setup is authorized, targeted round trips in a designated test project and a temporary test schedule. Capture actual return values and state changes, not only documentation claims. Coverage: A12, A13, A19 feasibility.

**Rollback:** remove only temporary test schedules/resources created during authorized validation; preserve their identities if cleanup fails. Capability discovery itself requires no project-data rollback.

### M1 — Draft the companion skill and conversational behavior

Define the skill's recognizable user goal and explicit operations: start a project, show the big picture, choose the next step, report progress, review, resume, pause, and finish. Keep these as natural language examples rather than mandatory commands.

Create the living-spec template and a short thesis example. Implement progressive decomposition in instructions: rough milestones first, current milestone detail next, normally one small recommended action. Include handling for unknown requirements, limited time, and exploratory work. Define a compact response pattern that connects the action to its parent outcome and completion condition.

Use fixture project data for evaluation. Mark simulated saves and reminders as simulations; they cannot count as Notion or scheduler integration success.

**Exit criteria:** an uncertain goal produces a useful draft without a long questionnaire; the next action fits a stated time budget and advances a visible milestone; non-coding projects require no software-specific ceremony.

**Verification:** evaluate a thesis conversation and one nonacademic project. Review outputs against A01–A03 and A17. Check that fictional external requirements are never presented as facts.

**Rollback:** return the staged skill files to the prior working version. No external data or schedules exist in this milestone.

### M2 — Establish Notion persistence and mutation recovery

Prepare the minimal project page, work-items structure, and activity log. Map parent/project links and dependencies to supported Notion properties, keeping infrequently used details in page bodies. Retain a single current-focus reference and explicit date types.

Implement the logical operations to load a project, query work items, save a spec, create/update items, append activity, and reload a project from its link. Carry stable operation identities across retried writes. Keep an operation record with intended changes, affected IDs, and confirmed steps so a partially applied change can be reconciled.

Refresh external state before mutation. Preserve unrelated user edits; surface detected same-field conflicts. Do not promise atomic write protection where the integration lacks it. Resolve ambiguous create outcomes before repeating creation, and do not replay a pending operation after a conflicting user edit without reconciliation.

**Exit criteria:** the authorized test project can be created/read/updated; a fresh session can reload it; repeated operations preserve one logical item/log entry; partial saves are reported accurately. The user can also inspect and edit the record in Notion.

**Verification:** targeted tests for pagination, stale reads, changed fields, denied access, interrupted writes, and an ambiguous create response. Use fixtures for failure cases and a small live round trip for supported integration behavior. Coverage: A10, A11, A13 persistence, A16.

**Rollback:** disable new writes and preserve a readable export or recorded before-state for affected records. Revert only known agent changes when their current values still match; resolve newer user edits rather than overwriting them. Do not erase project history or shared content.

### M3 — Complete the progress and replanning loop

Connect skill behavior to persisted work-item states. Add partial progress, clear completion, ambiguous “done,” blocked work, reopening, dropped work, and accepted scope changes. Validate same-project parent links and dependency cycles before recommending affected work.

Review parent completion criteria after child completion. Keep completed outcomes distinct from action counts. Support pause/resume and reload the project before choosing an action after a context reset. Preserve hard deadlines while proposing recovery plans.

**Exit criteria:** a user can maintain the project through “I have 10 minutes,” “done,” “stuck,” and “the scope changed,” with one focused clarification when needed. The loop produces truthful Notion updates and never treats silence or elapsed time as completion.

**Verification:** execute the thesis journey through partial work, a blocker, accepted scope revision, a reopened action, and a new session. Include parent criteria unmet despite completed children and invalid hierarchy fixtures. Coverage: A04–A11, A15 conversational recovery, A17, A18.

**Rollback:** restore the previous skill behavior and disable faulty mutation paths. Reconcile affected records from the activity log and before-state. Preserve user reports and artifacts even if task structure is revised.

### M4 — Add scheduled check-ins and lifecycle controls

Use the host's existing scheduler and notification channel. Each schedule carries a stable project reference and reloads current Notion state on execution. Activate only after the user opts in and agrees to timezone, cadence, notification intent, and quiet hours.

Support one agreed weekly review initially, plus on-demand check-ins. Keep explicit periodic reviews distinct from quiet monitoring. An active weekly review may deliver at each requested occurrence; monitoring notifies only for meaningful findings. Enforce the delivery semantics established in M0.

Persist the returned schedule identity immediately and reconcile partial setup before creating another schedule. Add pause, snooze, resume, cancellation, project completion/abandonment, and runtime-unavailable recovery. A paused/closed project suppresses companion-authored check-ins even if disabling its external schedule is still pending; failed scheduler changes remain visible.

**Exit criteria:** a real scheduled test run reloads current project state and delivers the expected check-in; schedule changes are verified against host state; retries and missed runs behave according to the retained or explicitly revised A13 requirement.

**Verification:** a temporary short-lived schedule tests actual execution and delivery, then is disabled/cancelled and verified. Failure fixtures cover schedule created but binding save failed, cancellation failed, repeated occurrence, and a crash around notification delivery. Coverage: A12–A15, A19.

**Rollback:** disable/cancel schedules by their stored identities before reverting scheduler behavior. If cancellation fails, report the actual state and give the specific manual control required. Preserve schedule bindings until cleanup is confirmed; do not create replacements during uncertainty.

### M5 — Verify and package for a pilot

Run the requirement-focused checks and conversations for the completed implementation. Consolidate results into an A01–A19 matrix with evidence and explicit failed/unverified items. Repeat checks only when a change, failure, or unresolved concern justifies it.

Prepare the staged skill package, Notion-template setup guidance, host adapter notes, known limitations, and install/remove instructions. Validate the package using the current skill-creation workflow when implementation reaches this milestone. Installation into the user's skill directory is a later authorized setup action.

**Exit criteria:** all applicable acceptance cases pass, with any spec revision explicitly recorded. A live test demonstrates Notion persistence and actual scheduler behavior; fixture-only success is insufficient. No unresolved conflict, unconfirmed write, or test schedule remains hidden in the delivery report.

**Rollback:** restore the prior installed skill if one exists, or remove only this skill's installed files. Cancel its schedules first. Preserve the Notion project for manual use and export; skill removal must not delete the user's work.

### M6 — Run the two-week pilot

Use one real project after setup is authorized. Agree to the default timezone proposal (`Asia/Jakarta` for this user), cadence, and routine-write policy. Keep the pilot bounded to its selected project.

Track the specification's initial signals: at least three sessions with saved progress, successful resumption after a context reset, and a delivered agreed check-in. Ask whether starting and reporting progress required less effort and whether reminders were useful. Treat these as learning targets, not manufactured success metrics.

**Exit criteria:** a brief pilot report identifies useful behavior, friction, failures, and one recommended next change. Consider Calendar or a dedicated app only if observed friction justifies it.

**Rollback:** pause or stop the companion and verify schedule shutdown. Preserve all Notion records so the user can continue manually.

## Verification approach

Use checks that test requirements rather than duplicating implementation details:

- Conversational evaluations assess invented requirements, action size, ambiguity handling, helpfulness, and progressive detail. Review generated wording using a rubric rather than exact-text assertions.
- If supporting code is introduced, test state invariants, graph validation, operation reconciliation, and adapter contracts. Instruction-only files do not need an artificial unit-test suite.
- Integration checks verify actual external reads/writes and scheduler lifecycle in a designated test project. Fault injection covers failures that are impractical or harmful to reproduce live.
- No automated test can establish whether reminders help this person; assess that during the pilot.

| Acceptance coverage | Main verification stage |
| --- | --- |
| A01, A02, A03 | M1 conversational evaluations |
| A04, A05, A06, A07, A08, A09 | M3 progress/replanning |
| A10, A11 | M2 persistence plus M3 full-flow resumption |
| A12 | M0 scheduling feasibility plus M4 live check-in |
| A13 | M0 semantics decision, M2 retry handling, M4 notification retry/crash cases |
| A14, A15 | M3 state/recovery plus M4 schedule lifecycle |
| A16 | M2 failed/partial persistence |
| A17, A18 | M1/M3 truthful progress and hierarchy validation |
| A19 | M0/M4 partial scheduler operations |
| All A01–A19 | M5 final evidence matrix |

## Decisions and remaining uncertainty

The next implementation action would be M0 capability validation, with M1's portable draft available as independent work. No additional product-scope questions are needed to deliver this plan.

Resolve these before dependent implementation:

1. **Initial host:** Codex-first remains an assumption; user preference determines the adapter.
2. **Notion access:** select and validate a writable supported integration. Searching pages alone does not satisfy the specification.
3. **Reminder guarantees:** establish occurrence identity, delivery behavior, and concurrency limits. A skill cannot manufacture guarantees its tools do not provide.
4. **Setup preferences:** select the project, authorize routine project writes, and agree to check-in settings when the user starts setup.

There is no promised effort estimate until M0 establishes whether existing tools are sufficient. Work on an unsupported requirement remains visibly incomplete rather than being counted as a successful first release.

## Documentation and observations

Reviewed on 14 October 2026. Capability verification in M0 remains necessary even where documentation describes a feature.

- [Specification v0.1](project-companion-spec.md) supplies behavioral requirements and A01–A19.
- [Notion update-page documentation](https://developers.notion.com/reference/patch-page) establishes that updating content requires the connection's update-content capability.
- [OpenAI scheduled-tasks documentation](https://learn.chatgpt.com/docs/automations?surface=app) describes skill-backed and chat-attached scheduling, plus local-runtime availability constraints.
- Inspection found an exposed automation-management tool and no currently callable Notion tools; no account was queried and no schedule or external project was created.
