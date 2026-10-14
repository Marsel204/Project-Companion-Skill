# Project Companion Skill

An AI project companion that turns goals into small actions, tracks reported progress in Notion, and follows up with agreed scheduled check-ins.

Use it for a thesis, research project, event, moving house, or another personal project. It connects **goal → milestones → tasks → next actions**, so you can see the big picture and have a manageable first step.

## Install in Codex

Ask Codex:

> Use $skill-installer to install the skill from https://github.com/Marsel204/Project-Companion-Skill/tree/main/skills/project-companion

The skill directory is [`skills/project-companion`](skills/project-companion). Its entry point is [`SKILL.md`](skills/project-companion/SKILL.md). Refresh skills or start a new chat if discovery has not picked up the installation.

## Use

Start a project:

> $project-companion Help me finish my thesis proposal in six weeks. I haven't chosen a research question yet. Help me define the goal and choose a small first step.

Continue in the same project chat:

- “I have 15 minutes today.”
- “I drafted two of the three questions.”
- “I'm stuck because I can't access the data.”
- “My supervisor changed the scope.”
- “Show my progress and what's next.”

The companion clarifies requirements, keeps future milestones concise, and expands the work you are currently doing. Partial work stays in progress. Completing an action prompts a review of its parent outcome rather than automatically completing the whole milestone.

## Connect your tools

Planning works in chat immediately. Persistent records and reminders require host integrations:

1. **Notion:** install/connect a writable Notion integration in your host, authorize your workspace, and designate a project page. The companion verifies available capabilities before creating or updating records.
2. **Check-ins:** request a cadence, local time, and timezone. For example: “Check in every Friday at 7pm, Asia/Jakarta.” The host scheduler must actually create and confirm the schedule.

The skill supplies workflow instructions; the host supplies app access, execution, and notifications. It reads current Notion state when you return or when an agreed check-in runs. The offline helper supplies no app access and sends no notifications.

No Notion account or reminder schedule is connected by installing this repository. Live integration behavior has not been verified. Local runs requiring your computer depend on the computer and desktop app being available. Unconditional exactly-once external notification delivery is not established by the offline checks.

Google Calendar, a standalone app, collaboration, and cross-project prioritization are deferred.

## Package contents

| Path | Purpose |
| --- | --- |
| `skills/project-companion/SKILL.md` | Main skill instructions |
| `skills/project-companion/references/` | Workflow, Notion, check-ins, Codex routing, and helper details |
| `skills/project-companion/assets/` | Project/check-in templates and fictional example data |
| `skills/project-companion/scripts/project_state.py` | Offline validation and state transformations |
| `skills/project-companion/evals/conversations.json` | Eight behavioral requests and rubrics for future agent evaluation |
| `tests/` | Local requirement-focused state tests |
| `docs/` | Original design drafts and current verification status |

## Test

From the repository root:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Requires Python 3.10+ and IANA timezone data. The helper and tests otherwise use only the standard library. The official optional skill validator uses PyYAML in its own environment.

The local suite covers partial progress, ambiguous completion, parent criteria, blockers, revisions, field conflicts, hierarchy/dependency validation, and serialized occurrence handling. See [verification status](docs/verification.md) for coverage and integration limits. The conversation rubrics are prepared cases, not passing independent model evaluations.

## Design

- [Specification](docs/project-companion-spec.md)
- [Implementation plan](docs/project-companion-plan.md)

The design documents preserve the initial draft and planning context. Current delivered behavior and verification status are described above and in the verification report.
