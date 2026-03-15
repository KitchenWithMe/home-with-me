# HomeWithMe Schema

## Household Directory

Use `$HOME/.homewithme/` for all runtime data.

- `config.yaml`: stable household configuration
- `state/current.json`: rebuildable runtime snapshot
- `events/YYYY-MM.jsonl`: append-only event history
- `outputs/YYYY-MM-DD-plan.md`: rendered plan for humans
- `outputs/YYYY-MM-DD-plan.json`: rendered plan for automation

## Config Structure

Top-level keys:

- `household`
- `members`
- `tasks`

### Members

Each member should support:

- `id`
- `display_name`
- `aliases`
- `roles`
- `fixed_rest_weekdays`
- `low_load_weekdays`
- `blackout_dates`
- `blackout_ranges`

### Tasks

Each task should support:

- `id`
- `name`
- `area`
- `cleaning_band`
- `frequency_label`
- `aliases`
- `default_assignee`
- `backup_assignees`
- `rest_day_policy`
- `tier`
- `cadence`

### Suggested `area` values

- `bedroom`
- `kitchen`
- `bathroom`
- `living_room`
- `whole_home`

### Suggested `cadence` shapes

- `{"type": "range_days", "min_days": 1, "max_days": 3, "default_days": 2}`
- `{"type": "times_per_week", "value": 2}`
- `{"type": "interval_weeks", "value": 2}`
- `{"type": "range_weeks", "min_weeks": 3, "max_weeks": 4, "default_weeks": 3}`
- `{"type": "range_months", "min_months": 1, "max_months": 2, "default_months": 1}`
- `{"type": "interval_months", "value": 3}`

## Event Types

- `config_initialized`
- `task_completed`
- `task_deferred`
- `task_skipped`
- `task_reassigned`
- `daily_plan_generated`
- `member_availability_updated`
- `task_rule_updated`

## Output Contract

Daily-plan Markdown should always include:

- `必做`
- `建议做`
- `可选做`
- `说明`
