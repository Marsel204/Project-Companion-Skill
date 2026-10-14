# Codex host adapter

The workflow is portable; this reference supplies the first host's routing. Discover available tools in the active session and use their current schema. Do not hard-code a tool availability assumption into the conversation.

## Notion

Discover writable Notion tools if exposed. Follow [Notion mapping and recovery](notion.md). If absent or read-only, report the capability gap and offer the unsaved draft. The skill does not install a connector, connect an account, or acquire secrets automatically.

## Scheduled follow-up

Use the exposed automation-management tool, commonly `mcp__codex_app__automation_update`. For an ongoing project conversation, prefer its chat-attached heartbeat form when supported. Use native tool calls; never emit raw automation directives or manually write automation configuration.

Inspect the tool's actual return value for schedule ID/status. When updating an existing schedule, preserve unrelated settings, use its resolved ID, and avoid duplicate schedules. Use supported scheduler view/update/delete operations to verify changes; do not infer that “a tool call was made” means the change succeeded. Keep the returned identity if a later Notion write fails.

If local files are required by a scheduled run, the computer and desktop app need to be running. Scheduling availability, unattended Notion access, trustworthy occurrence identity, and delivery acknowledgments must be checked for the chosen account/runtime. This package has not connected to a user's Notion workspace or validated a live check-in.

Notification policy comes from the user's stated intent. Honor mute/unmute through actual tool controls. A requested periodic review differs from quiet monitoring; see [check-ins](check-ins.md).

## Skill and helper paths

Resolve resource paths relative to this skill's directory, independent of the project's current working directory. Run the helper using its absolute path; place request/result working copies under the project's working directory, not in the installed skill folder. Never overwrite Notion state with a local cache without reloading and reconciling current state.

The helper uses Python 3.10+ standard-library modules and the machine's IANA timezone database. If timezone data is unavailable, report that dependency rather than changing the timezone silently. Other hosts can replace tool routing while reusing the core workflow and templates; compatibility with them has not been exercised.

Reference: [OpenAI scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app).
