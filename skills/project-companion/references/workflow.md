# Conversational workflow

## Intake

Start with the desired outcome, the reason it matters, and the starting point. Ask about externally required deliverables or dates when they matter. Mark assumptions and unknowns instead of filling them with invented facts. A thesis may start with feasibility exploration before its research question is specified.

Draft a small living spec and a milestone map. Each milestone names an outcome and completion criteria. Keep future branches coarse. Under the current milestone, create tasks and small actions with a useful result. A new user's draft is usable in chat while integration setup remains incomplete.

Suggested questions: “What would you like to have finished?”, “Is there a firm deadline or required format?”, “What have you already done?” Ask fewer when the conversation supplies the answers. After the first substantive answers, provide a draft and action; after two answer turns, a long intake questionnaire should not still block starting.

## Next action

Reload the project and current focus. Check work-item dependencies and ancestors. Consider deadline risk, the user's chosen focus, and whether an unblocking action would help more. Offer one recommended action and up to two alternatives when they aid a real choice. Explain the link to the larger outcome in one sentence.

For “I have 10 minutes,” pick a feasible result, not a relabeled long task. The helper can shortlist existing actions; the agent supplies judgment, estimates, and useful decomposition. If nothing is ready, propose an unblocking or exploratory action.

## Updates

| User report | Record and next response |
| --- | --- |
| “Two of three questions drafted” | In progress; preserve the two drafts and remaining work. |
| “Done” with one clear action | Done, source: user report; review parent criteria. |
| “Done” with ambiguous targets | Ask which action; leave statuses unchanged. |
| “Stuck; data access is unclear” | Blocked with the reason; offer an access-check action or ready alternative. |
| “That was marked done by mistake” | Reopen and retain earlier reports/artifacts. |
| “We no longer need this task” | Dropped with the reason; retain history and resolve dependents. |
| “My supervisor changed the scope” | Draft affected spec/milestone changes, accept corrections, then save accepted changes. |

No state changes are inferred from silence, a date passing, or a check-in firing. Evidence may be a report, note, link, or file; distinguish self-report from verified artifact contents. Never call a supplied URL proof of completion without assessing the relevant criterion.

## Review, recovery, and finish

Summarize completed milestone outcomes, focus, blockers, and the next step. If useful, display counts explicitly as work-item counts; never convert arbitrary action counts into overall project completion.

After missed work, offer a smaller step, a different focus, a new target date, or pause. Hard external deadlines remain fixed unless the user explicitly changes them. Propose recovery without guilt or escalating reminder frequency.

Paused projects preserve progress and stop check-ins. Resuming a project does not silently reactivate an old schedule; confirm the user's requested cadence and verify actual scheduler state. For project completion, review success criteria and confirm the outcome with the user, then stop the schedule. Completion may coexist with dropped or unnecessary unfinished tasks if the outcome is met; explain that decision.
