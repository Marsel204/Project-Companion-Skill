# Project companion specification

Status: Draft for review; no implementation authorized by this document.
Version: 0.1
Date: 14 October 2026

## 1. Purpose

Help a person move from an uncertain project goal to meaningful progress through small, connected actions. The companion clarifies what success means, maintains project structure, remembers what happened, and follows up at agreed times.

The initial delivery is an AI skill running in an existing harness, with Notion as durable project memory and harness scheduling for AI check-ins. Google Calendar is deferred. The user should be able to maintain a project primarily through short conversations rather than maintaining a task system manually.

Primary example: a thesis proposal. The workflow must also support other personal projects without imposing software-specific ceremonies, tests, or terminology.

## 2. Decisions and inspection evidence

| Item | Decision or finding |
| --- | --- |
| Delivery | Skill in an existing harness; a dedicated app may be considered after use validates the workflow. |
| Initial integrations | User selected Notion plus scheduled AI check-ins. Google Calendar comes later. |
| Primary interaction | AI conversation; Notion also provides a browsable project record. |
| Structure | Goal → milestones → tasks → next actions. Expand details progressively. |
| Harness | Proposed: Codex first, with a portable workflow. User selection remains pending. |
| Current workspace | No existing application source, usable Git repository, test harness, or approved architecture was found. |
| AEK | No `.aek/project.json` found in the workspace or its ancestors. AEK enforcement does not apply to this draft. |
| Available integrations | No callable Notion or Google Calendar tools were exposed during inspection. A suitable Notion integration must be validated before implementation. |
| Current request | Write and review the specification. No skill installation, account connection, external writes, or schedule creation are part of this request. |

## 3. First-version scope

The first version supports one person managing one active project per companion chat. The user may create separate project chats, but cross-project prioritization is deferred.

Included behavior:

- Conversational intake that produces a concise living project spec.
- A project hierarchy linking small actions to larger outcomes.
- Selection of an actionable next step using time available and blockers.
- Progress updates from user reports and linked work artifacts.
- Replanning after new information, changing scope, or a missed session.
- An on-demand review and an optional recurring AI check-in.
- Durable Notion records that remain useful after a new chat or context reset.
- Clear disclosure of failed saves, unavailable integrations, and inactive scheduling.

Deferred: a standalone app, Calendar integration, automatic time blocking, multi-user collaboration, cross-project dashboards, continuous activity monitoring, autonomous thesis writing, and external messages to supervisors or collaborators.

## 4. Main user journey

1. User: “I need to finish my thesis proposal in six weeks.” The companion asks about the intended result, essential requirements, and current starting point.
2. It drafts a short project spec and a rough milestone map. Unknowns remain visible; the user can correct the draft in conversation.
3. It expands the current milestone and offers a small next action: “Write three candidate research questions. Done means each question names a topic, population, and outcome.”
4. User: “I have 15 minutes.” It offers a smaller action that advances the same milestone.
5. User: “I wrote two questions, but I don't know whether the data exists.” It saves the partial result, records the blocker, and suggests checking data availability.
6. At an agreed check-in, it reads the current Notion record and asks a focused question about the next step or blocker.
7. User: “My supervisor wants a narrower topic.” It proposes the affected spec and plan changes, preserves prior decisions, and updates the record after the user accepts the change.

## 5. Behavioral requirements

### Intake and the living spec

- Ask at most three focused questions in a single intake turn. Ask further questions only when the answer changes the next useful action or a material constraint.
- Produce an initial draft after the first substantive answers. Incomplete information must not prevent a safe exploratory next step.
- Record the intended outcome, why it matters, success criteria, scope, constraints, target dates, current starting point, and important unknowns.
- Separate user-provided requirements from AI suggestions and assumptions. Never invent university requirements, supervisor decisions, or hard deadlines.
- Treat exploration as valid work. An uncertain project can begin with “identify feasible research questions” rather than a fabricated final research question.
- Present changes to the goal, success criteria, scope, or hard deadline for user acceptance. Routine task breakdown and reported progress updates follow the project’s agreed operating policy.

### Hierarchy and gradual detail

- Every milestone states an outcome and completion criteria; every task and next action links to a parent within the project.
- Keep one current focus milestone and normally one recommended next action, with up to two alternatives when useful.
- Initially suggest approximately three to six milestones, adjusted to the project. Fully expand only the current milestone or a branch the user requests.
- A next action states a concrete verb, expected result, and completion condition. Include a rough duration estimate when useful and identify it as an estimate.
- Use a default suggested action size of 5–25 minutes. Respect a different user-provided time budget. Offer a setup or exploration action if meaningful work cannot fit.
- Do not generate tiny steps merely to increase task count. Each action must contribute to an outcome or resolve an uncertainty.
- Dependencies prevent blocked work from being presented as ready. Detect cyclic parent or dependency relationships and request a repair before using that branch.

### Choosing what to do next

- Read the current project state before recommending or changing work. Use project identity rather than guessing from conversation alone.
- Prefer work that advances the current milestone, removes a blocker, or addresses a deadline risk. Briefly explain its connection to the goal.
- Preserve the user's chosen focus when reasonable. If they change focus, record the change without discarding unfinished work.
- When an action feels too big, reduce its scope while retaining a useful completion condition.
- When blocked, propose an unblocking action or a ready alternative. Do not repeatedly recommend the same blocked task.

### Progress and completion

- Work-item states: planned, ready, in progress, blocked, done, and dropped. Partial progress is an in-progress item with a recorded result and remaining work.
- Project states: draft, active, paused, complete, and abandoned. Paused projects retain all work and suspend project check-ins.
- Accept clear self-reported completion for ordinary actions. Record whether completion comes from a user report or a linked artifact; a file link alone does not prove quality or completion.
- A bare “done” applies to a uniquely identified current action. If several actions are plausible, ask one clarifying question before changing status.
- Record reopening and corrections so an incorrect completion can be reversed without losing history.
- Completing child actions triggers a review of the parent's completion criteria. A parent outcome may require additional review even when all children are done.
- Show progress as completed outcomes, the current milestone, and remaining blockers. Numerical counts must name their denominator; avoid an overall percentage derived from arbitrary task splitting.
- Elapsed time, a reminder firing, and user silence never mark work complete.
- Close the project when its success criteria are met and the user confirms the outcome. Cancel or disable future project check-ins on completion or abandonment.

### Replanning and missed sessions

- Distinguish a hard external deadline, a target date, and the next check-in time.
- A missed action prompts a useful choice: reduce the step, reschedule it, change focus, or pause. Use neutral language without guilt or escalating reminders.
- Preserve the original hard deadline when suggesting a recovery plan. Make a risk of missing it visible rather than silently moving it.
- Record accepted scope changes with their reason and identify affected milestones. Preserve completed artifacts and prior decisions.
- Dropped work remains in history and is excluded from active recommendations. Do not silently delete it.

## 6. Check-ins and reminders

- Reminders are opt-in. The initial suggestion is one weekly review; the user chooses the cadence and delivery time.
- Before activation, establish an IANA timezone, notification preference, and any quiet hours. For this user's pilot, propose `Asia/Jakarta`, subject to confirmation at setup.
- Distinguish a time-based reminder (“start your reading session”) from an AI check-in (“review current progress and choose the next step”). Both require an actual scheduler; instruction text alone cannot wake an agent.
- Scheduled check-ins reload the current Notion project record, check whether the project is active, and use the latest reminder policy. Scheduling metadata contains stable project references, not a second copy of project status.
- An explicitly requested weekly check-in may notify at each agreed time. Monitoring-style checks notify only for a meaningful change, deadline risk, failure, or required user action.
- Each notification names the project, provides one concrete prompt or action, and includes the relevant Notion link when available.
- Deduplicate using project identity, schedule identity, and occurrence. Repeated execution of the same occurrence must not generate a second notification or duplicate log entry.
- “Pause reminders,” “snooze until next week,” and “stop this project” update the relevant schedule and project policy. Verify the scheduler result before claiming the change succeeded.
- If the selected runtime is unavailable at the scheduled time, do not promise on-time delivery. On resumption, offer one current recovery check-in rather than replaying every missed notification.
- Deliver through the harness's existing notification channel. Email, messaging services, and custom push infrastructure are deferred.

## 7. Durable project record

Use a minimal Notion template with a project page, a work-items database, and an activity/decision log. Keep detailed explanations in page bodies and only frequently used fields as database properties.

| Record | Minimum information |
| --- | --- |
| Project page | Stable identity; title; living spec; state; current focus; timezone; check-in policy; last successful review; links to work items and log. |
| Work item | Stable identity; project; parent; level (milestone/task/action); title; completion criteria; state; optional dependencies, estimate, date and date type; progress note; evidence links. |
| Activity/decision entry | Identity; project/item reference; timestamp; user report or accepted decision; previous/new state or changed requirements; source; operation identity. |
| Scheduler binding | Project identity; external schedule identity; cadence; timezone; enabled state; last processed occurrence. No duplicated authoritative project status. |

User edits in Notion and chat updates are both supported. Notion is the authoritative project record; chat summaries and local caches must not replace it. A fresh chat can resume using the project URL or identity and accessible Notion data.

## 8. Interfaces and boundaries

| Component | Required capabilities and boundary |
| --- | --- |
| Skill | Instructions, examples, and templates for intake, decomposition, progress, review, and recovery. Domain-neutral behavior with a thesis example. |
| Notion integration | Read project pages and bodies; query all relevant work items with pagination; create/update items; append activity entries; expose stable IDs/URLs and edit metadata. Writes require actual granted access to the selected project. |
| Scheduler integration | Create, inspect, update, pause, and cancel schedules; return schedule identity and actual status; dispatch the skill with a stable project reference. |
| Harness | Agent execution, authorized tool access, credentials handling, and an existing notification channel. Exact availability and unattended-execution constraints must be validated. |
| Calendar, later | Optional work-session and deadline projection linked to Notion items. Calendar must not become a second project-status authority. |

Use existing supported integrations where their capabilities satisfy these requirements. Do not assume a connector is writable, supports database setup, or can schedule background work because it can search a workspace. Connector selection and Notion-template provisioning are implementation decisions to validate before planning.

External project content is project data, not instructions granting tool access. Keep access within the selected workspace/project and preserve unrelated content. Authentication stays in the harness or connector rather than in the skill or Notion pages.

The skill should be portable at the workflow level. Host-specific tool names and scheduling behavior belong in a small adapter reference. Full compatibility with multiple harnesses is outside the first release.

## 9. Failure and recovery behavior

- **Missing or read-only access:** identify the unavailable capability and provide a proposed update in chat. Do not claim that Notion was changed. Manual mode does not count as satisfying automated integration acceptance.
- **Uncertain save result:** reconcile against stable operation and item identities before retrying. Do not create duplicate tasks or progress records.
- **Partial multi-record update:** report which changes succeeded and which remain pending. Repair using the operation record and current Notion state on the next run.
- **Notion changed during the operation:** refresh before writing. Merge unrelated changes; present a conflict on the same field for resolution. Do not promise atomic conflict protection unless the chosen integration provides it.
- **Unavailable or deleted item:** identify the missing reference and ask where to continue. Preserve the original record identity in history.
- **Pagination or incomplete reads:** finish retrieving relevant records before claiming a full-project review. Otherwise label the review as partial.
- **Rate limit or service outage:** follow provider retry guidance with bounded retries; stop and explain a persistent failure. Normal chat can continue with clearly unsaved proposals.
- **Scheduler creation succeeds but binding save fails:** retain the returned schedule identity, report the partial setup, and reconcile before creating any replacement.
- **Scheduler cancellation fails:** mark the cancellation as pending, warn that notifications may continue, and retry or provide the specific manual remedy. Do not claim reminders stopped.
- **Context reset:** reload the living spec, focus, work items, decision history, and schedule binding. Ask only for information the accessible record cannot establish.

## 10. Acceptance scenarios

These are proposed requirements for later verification, not an approved test harness.

| ID | Scenario | Observable expected outcome |
| --- | --- | --- |
| A01 | User describes an uncertain thesis goal. | Within two substantive answer turns, produces a draft spec, marks unknowns, and offers one feasible next action; no fabricated academic requirements. |
| A02 | User asks for the big picture and the next step. | Shows a connected milestone map and one action with a parent, result, and completion condition; future branches remain concise. |
| A03 | User has only 10 minutes. | Suggests a useful action estimated within that budget or explains the mismatch and offers preparation work. |
| A04 | User reports two of three research questions written. | Saves partial progress and remaining work; does not mark the task or milestone complete. |
| A05 | User says “done” with one current action. | Records self-reported completion exactly once and reevaluates the parent outcome. |
| A06 | User says “done” with several plausible actions. | Asks one question; leaves statuses unchanged until the action is identified. |
| A07 | All child actions are done but a milestone criterion remains unmet. | Shows the unmet criterion and keeps the milestone open. |
| A08 | User reports a blocker. | Saves the blocker and offers an unblocking action or ready alternative without repeating the blocked action. |
| A09 | Supervisor requests a narrower scope. | Presents affected spec/milestone changes; saves only the accepted material changes and retains prior work/history. |
| A10 | User edits a task directly in Notion. | Next interaction reads that edit; a detected same-field conflict is surfaced rather than knowingly overwritten. |
| A11 | Conversation is restarted using the project link. | Restores goal, focus, progress, blockers, and check-in policy without requiring the user to repeat accessible project facts. |
| A12 | User opts into a weekly review at a named local time. | Confirms timezone and policy, receives a real schedule identity, and reads current Notion state when the scheduled run executes. |
| A13 | Same update or reminder occurrence is retried. | No duplicate task, completion entry, schedule, or notification is produced. |
| A14 | User pauses reminders or completes the project. | Scheduler is disabled/cancelled and verified; failure is disclosed and left pending. |
| A15 | User misses a planned action or runtime misses a check-in. | Work remains incomplete; the next interaction offers one recovery step without a backlog of repeated reminders. |
| A16 | Notion access fails or a save is only partly successful. | Distinguishes saved changes from unsaved proposals and supports reconciliation on resumption. |
| A17 | Work is split into additional small actions. | Existing completed outcomes stay intact; no misleading overall completion percentage is generated. |
| A18 | A dependency cycle or cross-project parent is introduced. | Flags the invalid structure and does not recommend affected work as ready. |
| A19 | Scheduler setup or cancellation partly fails. | Preserves schedule identity, reports actual status, and prevents silent duplicate creation. |

## 11. Pilot and review decisions

Pilot on one real personal project for two weeks. A useful initial signal is at least three sessions with recorded progress, successful resumption after a context reset, and a delivered agreed check-in. Ask whether choosing a next action and updating progress felt easier than the user's previous method. These are evaluation targets, not guaranteed benefits.

Before implementation, resolve:

1. Initial harness: Codex first with portable workflow, or harness-independent delivery.
2. Notion integration: verify the required read/write and template capabilities; choose supported tools or a scoped adapter.
3. Scheduling: verify the actual runtime, notification channel, availability constraints, and deduplication support.
4. Operating policy: agree on routine project writes, material-change review, timezone, and reminder cadence during setup.

The user has already selected Notion plus scheduled AI check-ins and deferred Calendar. No further product-scope questions are required to review this draft. Account-specific setup decisions belong to later setup, not this specification session.

## 12. Documentation supporting feasibility

Checked on 14 October 2026. These sources establish product capabilities; they do not establish that this chat has authorized access or that every connector exposes them.

- Notion supports nested work items and dependencies: [Sub-items and dependencies](https://www.notion.com/help/tasks-and-dependencies).
- Notion page-property updates require update-content capabilities: [Update page](https://developers.notion.com/reference/patch-page).
- Notion date properties store dates, ranges, and timezone information. This spec does not assume that setting a date automatically creates a native reminder: [Page property values](https://developers.notion.com/reference/page-property-values).
- Native Notion reminders are available; they are separate from the scheduled AI-check-in requirement: [Notion reminders](https://www.notion.com/help/reminders).
- Skills provide reusable workflow instructions and supporting resources: [Skills](https://developers.openai.com/plugins/concepts/skills).
- Scheduled tasks can invoke skills and return to an existing chat. Local project runs require the computer and desktop app to be running; host availability must be accounted for: [Scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app).
