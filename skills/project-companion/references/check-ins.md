# Check-ins and reminder delivery

## Configure only when requested

Confirm the user's requested cadence/local time, IANA timezone, quiet hours, and notification intent. Suggest one weekly review without activating it by default. The device timezone is a suggestion, not a permanent skill setting.

A review explicitly requested every week may notify every agreed occurrence. A monitoring loop stays quiet when nothing meaningful changed; notify for a meaningful change, deadline risk, failure, or required user action. Store notification preferences in the host's controls and the project policy, using the controls that actually exist.

Use the host scheduler and existing notification channel. A Markdown due date does not wake an agent. Do not create custom cron jobs or a separate notification service as a workaround. Check local-runtime availability limits before promising delivery while the user's computer is off.

Use [the check-in prompt template](../assets/checkin-prompt.md), replacing the project references and review intent with actual agreed values. Save the returned schedule identity immediately. Persist the binding before claiming activation succeeded. If scheduler creation succeeds but the Notion binding fails, preserve the returned ID in the recovery record and reconcile that existing schedule; do not create a replacement.

## On each run

Reload Notion policy, project state, current focus, pending operations, and occurrence record. Confirm the schedule still belongs to this project. Suppress companion-authored notifications for paused, complete, abandoned, or reminder-disabled projects. A native host may still emit a run banner; do not promise the skill can suppress host-owned notifications.

Compose one short check-in with a specific action/question and a project link. A missed runtime occurrence produces one current recovery check-in on resumption rather than a replay of every missed notification. Work does not become complete because a reminder fired.

## Duplicates and uncertain delivery

Use project ID + schedule ID + scheduled occurrence timestamp as a stable identity. Equivalent UTC offsets refer to the same occurrence. If the host cannot supply a trustworthy occurrence identity, automatic deduplication is unverified; do not invent one from the current clock for a retry.

In a serialized run with persistent storage, reserve the occurrence before sending. If it is already delivered, suppress repeat output. If reserved or delivery-unknown, stop repeated sending and reconcile the host's delivery record. Mark delivered only after actual delivery acknowledgment; a generated message or a helper return is not an acknowledgment.

The offline helper can test these decisions but cannot make reservation writes atomic in Notion or make notifications transactional. A crash after reservation may lose a message; a host may also emit its own duplicate banners. A13's unconditional no-duplicate guarantee remains unverified until host/storage behavior is established. Describe this honestly and seek a scoped requirement revision if necessary; do not quietly redefine A13 as passing.

## Pause, snooze, cancel, and resume

Immediately save disabled reminder policy, then pause/cancel the real schedule and verify actual scheduler state. Keep its ID and `cancellation_pending` until shutdown is confirmed. On failure, say notifications may continue and give the exact host control the user can use. Snoozing needs an explicit date/time and verified schedule change.

Close or abandon a project only as directed by the user; stop its schedules as part of that action. Preserve all project data. Re-enabling requires a real verified schedule; a project-state change alone does not restart it.
