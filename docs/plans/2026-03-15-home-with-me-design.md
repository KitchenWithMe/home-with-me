# HomeWithMe Design

## Summary

HomeWithMe is a single-household, stateful home-care skill that combines natural-language interaction with deterministic scheduling. The skill itself remains stateless; long-lived household data is stored under `$HOME/.homewithme/`.

The design follows a clear split:

- `SKILL.md` handles conversational behavior, clarification, and explanation.
- Python scripts handle deterministic storage updates, scheduling, and snapshot rebuilds.
- Household configuration, current state, event history, and generated outputs live outside the skill directory.

## Confirmed Scope

- Single household, single instance
- Household data stored in `$HOME/.homewithme/`
- Stable configuration separated from runtime state and history
- Runtime persistence uses append-only event logs plus a rebuildable current snapshot
- V1 uses pure natural-language interaction instead of explicit commands
- Members support canonical names plus aliases and role-based nicknames
- Daily plans are compatible with future automation, but automation is not part of V1

## Chosen Architecture

The design uses a rules-engine-first architecture.

- The language layer maps user input into structured intents.
- Deterministic scripts own initialization, scheduling, state changes, and snapshot rebuilding.
- Output explanations are generated from the same structured decisions used for scheduling.

This was chosen over prompt-only orchestration because the product requires repeatability, auditability, and long-term household state.

## Skill Layout

Recommended skill folder:

```text
home-with-me/
├── SKILL.md
├── agents/openai.yaml
├── scripts/init_household.py
├── scripts/generate_daily_plan.py
├── scripts/apply_event.py
├── scripts/rebuild_snapshot.py
├── references/schema.md
└── references/intent-patterns.md
```

The skill folder contains instructions and deterministic helpers. It does not store household-specific data.

## Household Data Layout

All household data is stored under:

```text
$HOME/.homewithme/
├── config.yaml
├── state/current.json
├── events/YYYY-MM.jsonl
└── outputs/
    ├── YYYY-MM-DD-plan.md
    └── YYYY-MM-DD-plan.json
```

### `config.yaml`

This file stores stable, user-maintained configuration:

- household metadata
- member definitions
- aliases and role labels
- availability rules
- task catalog
- task ownership defaults
- recurrence rules
- rest-day handling policy

It does not store dynamic fields such as `last_completed_at`.

### `state/current.json`

This file stores rebuildable runtime state:

- task status
- `last_completed_at`
- `next_due_at`
- deferrals and skip counters
- recent member load summaries
- rotation pointers
- latest daily-plan metadata
- snapshot version and rebuild timestamp

### `events/*.jsonl`

Event logs are append-only and provide auditability. Suggested event types:

- `config_initialized`
- `task_completed`
- `task_deferred`
- `task_skipped`
- `task_reassigned`
- `daily_plan_generated`
- `member_blackout_added`
- `member_availability_updated`
- `task_rule_updated`

If the snapshot is missing or stale, the system can rebuild from `config.yaml` plus event logs.

## Scheduling Model

The daily planner follows a fixed evaluation pipeline:

1. Load config, current snapshot, and recent events if needed.
2. Evaluate all active tasks and classify them as `overdue`, `due_today`, `upcoming`, or `optional_backlog`.
3. Evaluate each member's state for the target date.
4. Try the default assignee first.
5. Apply the task's `rest_day_policy` if the default assignee is unavailable.
6. Score each candidate assignment.
7. Enforce member daily capacity caps.
8. Output `required`, `recommended`, and `optional` task lists.
9. Persist plan outputs and append a `daily_plan_generated` event.

### Member Day-State Priority

The member day-state evaluation order is:

1. `blackout_dates` or `blackout_ranges` -> `unavailable`
2. `fixed_rest_weekdays` -> `rest_day`
3. weekend plus enabled weekend boost -> `weekend_boost`
4. `low_load_weekdays` -> `low_load_day`
5. otherwise -> `regular_day`

Weekend boost never overrides blackout or rest-day status.

### Assignment Scoring

The system should calculate two separate scores:

- `priority_score`: how important it is to do the task today
- `fit_score`: how suitable a given member is for that task today

`priority_score` considers:

- task tier weight
- overdue status
- overdue duration
- impact on household operations
- repeated deferrals caused by availability constraints
- recurrence pressure

`fit_score` considers:

- default ownership
- member preferences and aversions
- current day-state
- task intensity
- remaining daily capacity
- weekend suitability

### Rest-Day Policies

V1 supports:

- `try_backup_then_delay`
- `try_backup_then_unassigned`
- `delay_if_non_critical`
- `must_reassign`
- `hold_for_next_available_day`

Recommended defaults:

- critical operating tasks -> `must_reassign`
- light maintenance -> `try_backup_then_delay`
- deep cleaning -> `hold_for_next_available_day`
- optimization tasks -> `delay_if_non_critical`

## Natural-Language Interaction Model

V1 supports five primary intent groups:

- `initialize_household`
- `view_plan`
- `report_completion`
- `adjust_schedule`
- `update_rules`

The language layer must extract:

- `member_ref`
- `task_ref`
- `date_ref`
- `date_range_ref`
- `policy_change`
- `completion_time_ref`

Aliases are first-class entities. A single member can be referred to by canonical name, pronouns, or role labels such as `厨房主理人`.

## State-Change Rules

Natural-language input never edits state directly. Each confirmed interaction should:

1. append a structured event to the correct monthly JSONL file
2. refresh the snapshot through deterministic logic

Permanent rule changes also update `config.yaml` and emit a matching event.

If the language layer cannot disambiguate the member, task, or time reference, it must ask a clarification question before writing state.

## Output Contract

Daily plan output should always include:

- title
- `必做`
- `建议做`
- `可选做`
- `说明`

The explanation section explicitly calls out rest days, delays, and reassignments. Each task entry should explain both why it appears today and why it was assigned to that member.

The planner writes both Markdown and JSON outputs so future automations can either display the plan or consume it programmatically.

## Initialization Strategy

V1 uses guided setup as the primary path and structured import as a secondary path.

Guided setup should collect:

- household name and timezone
- members
- aliases
- rest-day rules
- low-load rules
- key rooms or zones
- recurring chores
- default and backup assignees

Structured import should initially support JSON and YAML. Spreadsheet and Markdown imports are deferred until later unless a minimal mapper is clearly necessary.

## Validation Strategy

Validation is split into two layers.

### Script-Level Validation

- initialization produces valid config and state files
- daily-plan generation is deterministic
- event application updates snapshot correctly
- snapshot rebuilding matches the expected runtime state

### Interaction-Level Validation

- common natural-language inputs map to the intended intent group
- aliases resolve to the correct member or task
- ambiguous inputs trigger clarification instead of incorrect writes

Representative validation prompts:

- `我洗完碗了`
- `男朋友刚倒了垃圾`
- `今天不做拖地，延到周末`
- `我周三周五休息，不要给我派任务`
- `这周末他不在家`
- `今天要做什么`

## Version Boundaries

### V1 Includes

- one household profile
- file-backed configuration and runtime state
- event log plus rebuildable snapshot
- daily-plan generation
- natural-language completion updates
- defer, skip, and reassign flows
- rest days, low-load days, blackout dates, and weekend boost
- default owner, backup owner, and lightweight rotation

### V1 Excludes

- multi-household support
- full spreadsheet ingestion
- learned preference models
- advanced monthly or quarterly recurrence DSLs
- push notifications
- graphical UI

### Likely V1.1 Work

- weekly overview output
- overdue backlog review
- richer recurrence rules
- fairness and load reports
- alias learning improvements
- scheduled daily generation through automation
