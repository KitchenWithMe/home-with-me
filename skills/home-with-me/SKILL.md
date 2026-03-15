---
name: home-with-me
description: Stateful home-care planning and household coordination skill for shared living. Use when Codex needs to manage recurring chores, member preferences, rest days, low-load days, blackout dates, daily task assignment, or natural-language household status updates backed by persistent local files.
---

# Home With Me

## Overview

Manage a single shared household with persistent local state stored outside the skill folder. Use deterministic scripts for initialization, scheduling, event updates, and snapshot rebuilds; use the language layer to clarify requests and explain decisions.

## Core Capabilities

- Maintain one household profile at `$HOME/.homewithme/`
- Track members, aliases, task ownership, cadence, and availability rules
- Generate daily chore plans with deterministic scheduling
- Accept natural-language status updates and rule changes
- Explain why a task was assigned, delayed, skipped, or reassigned

## Workflow

1. Resolve the household data directory at `$HOME/.homewithme/`.
2. Read `references/schema.md` before changing config or runtime state.
3. Route the user request into one of the supported intent groups:
   - initialize household
   - view today's plan
   - report completion
   - adjust schedule
   - update rules
4. If the user input is ambiguous, ask a clarification question before writing any state.
5. Use scripts for all deterministic state changes.
6. Explain the result in plain language, including why a task was assigned, delayed, or skipped.

## Data Layout

Keep household data out of the skill folder:

- `config.yaml` for stable household configuration
- `state/current.json` for rebuildable runtime state
- `events/*.jsonl` for append-only history
- `outputs/*.md` and `outputs/*.json` for generated daily plans

Never treat conversation memory as the source of truth when these files exist.

## Scripts

- `scripts/init_household.py`: create initial config, snapshot, and init event
- `scripts/generate_daily_plan.py`: generate today's plan and write outputs
- `scripts/apply_event.py`: append structured events and refresh current state
- `scripts/rebuild_snapshot.py`: rebuild current state from config plus events

## References

- `references/schema.md`: file layout, config schema, event types, output contract
- `references/intent-patterns.md`: high-frequency natural-language patterns and clarification rules

## Assets

- `assets/example-household.json`: bundled starter household for `init_household.py --example starter`

## Guardrails

- Ask clarifying questions before writing state when the member, task, or date is ambiguous.
- Prefer deterministic script output over ad-hoc reasoning for due dates, reassignment, and history updates.
- Keep replies explicit about what changed and why.
- Treat aliases as first-class references. A user may refer to one member by name, pronoun, or role label.
- When a user asks for today's chores, generate the plan from files instead of improvising from conversation context.
