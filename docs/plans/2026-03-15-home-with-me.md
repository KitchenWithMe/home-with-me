# HomeWithMe Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the `home-with-me` skill as a single-household, file-backed home-care assistant with natural-language interaction, deterministic scheduling, and auditable household history.

**Architecture:** The skill keeps conversational behavior in `SKILL.md`, while Python modules under `scripts/` own storage, scheduling, intent normalization, event application, and snapshot rebuilds. Household runtime data lives in `$HOME/.homewithme/`, split into stable config, rebuildable current state, append-only event logs, and generated plan outputs.

**Tech Stack:** Codex skill folder structure, Python 3 standard library, YAML/JSON/JSONL files, `pytest`, `@skill-creator`, `@test-driven-development`, `@verification-before-completion`

---

### Task 1: Scaffold The Skill Folder

**Files:**
- Create: `home-with-me/SKILL.md`
- Create: `home-with-me/agents/openai.yaml`
- Create: `home-with-me/scripts/`
- Create: `home-with-me/references/`

**Step 1: Generate the scaffold**

Run:

```bash
python /Users/blizhan/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  home-with-me \
  --path /Users/blizhan/data/code/opencode \
  --resources scripts,references \
  --interface display_name="HomeWithMe" \
  --interface short_description="Stateful shared-home care planning skill" \
  --interface default_prompt="Use $home-with-me to manage our shared-home chores and household rules."
```

Expected: a new `home-with-me/` folder with `SKILL.md`, `agents/openai.yaml`, `scripts/`, and `references/`.

**Step 2: Remove template filler and add missing directories**

Create these exact folders if the scaffold does not already include them:

```text
home-with-me/tests/
home-with-me/scripts/homewithme/
```

Expected: the skill has a place for internal Python modules and tests.

**Step 3: Validate the scaffold**

Run:

```bash
python /Users/blizhan/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/blizhan/data/code/opencode/home-with-me
```

Expected: validation passes without YAML or naming errors.

**Step 4: Commit**

```bash
git add home-with-me
git commit -m "chore: scaffold home-with-me skill"
```

### Task 2: Add Storage And Schema Tests

**Files:**
- Create: `home-with-me/tests/test_storage.py`
- Create: `home-with-me/scripts/homewithme/storage.py`
- Create: `home-with-me/scripts/homewithme/models.py`
- Create: `home-with-me/scripts/homewithme/__init__.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from homewithme.storage import default_household_paths, ensure_household_layout


def test_default_household_paths_point_to_home_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    paths = default_household_paths()

    assert paths.root == tmp_path / ".homewithme"
    assert paths.config == tmp_path / ".homewithme" / "config.yaml"
    assert paths.state == tmp_path / ".homewithme" / "state" / "current.json"


def test_ensure_household_layout_creates_runtime_directories(tmp_path):
    root = tmp_path / ".homewithme"

    ensure_household_layout(root)

    assert (root / "state").is_dir()
    assert (root / "events").is_dir()
    assert (root / "outputs").is_dir()
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_storage.py -q
```

Expected: fail with `ModuleNotFoundError` or missing functions.

**Step 3: Write minimal implementation**

```python
from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class HouseholdPaths:
    root: Path
    config: Path
    state: Path
    events_dir: Path
    outputs_dir: Path


def default_household_paths() -> HouseholdPaths:
    home = Path(os.environ["HOME"])
    root = home / ".homewithme"
    return HouseholdPaths(
        root=root,
        config=root / "config.yaml",
        state=root / "state" / "current.json",
        events_dir=root / "events",
        outputs_dir=root / "outputs",
    )


def ensure_household_layout(root: Path) -> None:
    (root / "state").mkdir(parents=True, exist_ok=True)
    (root / "events").mkdir(parents=True, exist_ok=True)
    (root / "outputs").mkdir(parents=True, exist_ok=True)
```

**Step 4: Run test to verify it passes**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_storage.py -q
```

Expected: both tests pass.

**Step 5: Commit**

```bash
git add home-with-me/tests/test_storage.py home-with-me/scripts/homewithme
git commit -m "feat: add home-with-me storage layout helpers"
```

### Task 3: Implement Household Initialization

**Files:**
- Create: `home-with-me/tests/test_init_household.py`
- Create: `home-with-me/scripts/init_household.py`
- Modify: `home-with-me/scripts/homewithme/storage.py`
- Create: `home-with-me/scripts/homewithme/config_io.py`

**Step 1: Write the failing test**

```python
import json

from homewithme.storage import default_household_paths
from init_household import build_initial_files


def test_build_initial_files_writes_config_state_and_init_event(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    payload = {
        "household": {"name": "HomeWithMe", "timezone": "Asia/Shanghai"},
        "members": [{"id": "mimi", "display_name": "咪咪", "aliases": ["我"]}],
        "tasks": [{"id": "wash-dishes", "name": "洗碗", "default_assignee": "mimi"}],
    }

    build_initial_files(payload)

    paths = default_household_paths()
    assert paths.config.exists()
    assert paths.state.exists()

    state = json.loads(paths.state.read_text())
    assert state["tasks"]["wash-dishes"]["status"] == "active"

    first_event = next(paths.events_dir.glob("*.jsonl")).read_text()
    assert "config_initialized" in first_event
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_init_household.py -q
```

Expected: fail because `build_initial_files` and config writers do not exist.

**Step 3: Write minimal implementation**

```python
def build_initial_files(payload: dict) -> None:
    paths = default_household_paths()
    ensure_household_layout(paths.root)
    write_config(paths.config, payload)
    write_initial_state(paths.state, payload)
    append_event(paths.events_dir, {"type": "config_initialized", "payload": payload})
```

Add the corresponding YAML write, JSON state bootstrap, and event-append helpers in `config_io.py` and `storage.py`.

**Step 4: Run test to verify it passes**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_init_household.py -q
```

Expected: the config file, snapshot, and event log are all created.

**Step 5: Commit**

```bash
git add home-with-me/tests/test_init_household.py home-with-me/scripts/init_household.py home-with-me/scripts/homewithme/storage.py home-with-me/scripts/homewithme/config_io.py
git commit -m "feat: initialize home-with-me household files"
```

### Task 4: Implement Event Application And Snapshot Updates

**Files:**
- Create: `home-with-me/tests/test_apply_event.py`
- Create: `home-with-me/scripts/apply_event.py`
- Create: `home-with-me/scripts/homewithme/events.py`
- Modify: `home-with-me/scripts/homewithme/storage.py`

**Step 1: Write the failing test**

```python
import json

from apply_event import apply_event_payload
from init_household import build_initial_files
from homewithme.storage import default_household_paths


def test_task_completed_updates_snapshot_and_appends_event(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    build_initial_files(
        {
            "household": {"name": "Test", "timezone": "Asia/Shanghai"},
            "members": [{"id": "mimi", "display_name": "咪咪", "aliases": ["我"]}],
            "tasks": [{"id": "wash-dishes", "name": "洗碗", "default_assignee": "mimi"}],
        }
    )

    apply_event_payload(
        {
            "type": "task_completed",
            "task_id": "wash-dishes",
            "performed_by": "mimi",
            "completed_at": "2026-03-15T09:30:00+08:00",
        }
    )

    paths = default_household_paths()
    state = json.loads(paths.state.read_text())

    assert state["tasks"]["wash-dishes"]["last_completed_at"] == "2026-03-15T09:30:00+08:00"
    assert state["tasks"]["wash-dishes"]["status"] == "done"
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_apply_event.py -q
```

Expected: fail because the event pipeline does not yet update runtime state.

**Step 3: Write minimal implementation**

```python
def apply_event_payload(event: dict) -> dict:
    state = load_state()
    if event["type"] == "task_completed":
        task = state["tasks"][event["task_id"]]
        task["last_completed_at"] = event["completed_at"]
        task["status"] = "done"
    append_event(...)
    save_state(state)
    return state
```

Expand this implementation to cover `task_deferred`, `task_skipped`, `task_reassigned`, and availability updates with shared handlers in `events.py`.

**Step 4: Run test to verify it passes**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_apply_event.py -q
```

Expected: snapshot and event log both reflect the change.

**Step 5: Commit**

```bash
git add home-with-me/tests/test_apply_event.py home-with-me/scripts/apply_event.py home-with-me/scripts/homewithme/events.py home-with-me/scripts/homewithme/storage.py
git commit -m "feat: apply home-with-me events to runtime state"
```

### Task 5: Implement Daily Scheduling

**Files:**
- Create: `home-with-me/tests/test_scheduler.py`
- Create: `home-with-me/scripts/generate_daily_plan.py`
- Create: `home-with-me/scripts/homewithme/scheduler.py`
- Modify: `home-with-me/scripts/homewithme/events.py`

**Step 1: Write the failing test**

```python
from homewithme.scheduler import generate_daily_plan


def test_generate_daily_plan_skips_member_rest_day_and_reassigns_critical_task():
    config = {
        "members": [
            {"id": "mimi", "fixed_rest_weekdays": ["sunday"]},
            {"id": "partner", "aliases": ["男朋友", "厨房主理人"]},
        ],
        "tasks": [
            {
                "id": "wash-dishes",
                "name": "洗碗",
                "default_assignee": "mimi",
                "backup_assignees": ["partner"],
                "rest_day_policy": "must_reassign",
                "tier": "critical",
                "cadence": {"type": "interval_days", "value": 1},
            }
        ],
    }
    state = {
        "tasks": {
            "wash-dishes": {
                "status": "active",
                "next_due_at": "2026-03-15",
                "last_completed_at": "2026-03-14T12:00:00+08:00",
            }
        }
    }

    plan = generate_daily_plan(config, state, target_date="2026-03-15")

    assert plan["required"][0]["task_id"] == "wash-dishes"
    assert plan["required"][0]["assignee_id"] == "partner"
    assert "休息日" in plan["notes"][0]
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_scheduler.py -q
```

Expected: fail because no scheduler exists.

**Step 3: Write minimal implementation**

```python
def generate_daily_plan(config: dict, state: dict, target_date: str) -> dict:
    required = []
    notes = []
    for task in config["tasks"]:
        if task_due_today(task, state, target_date):
            assignee = choose_assignee(task, config["members"], target_date)
            required.append(
                {"task_id": task["id"], "assignee_id": assignee["id"], "reason": "due_today"}
            )
            if assignee["id"] != task["default_assignee"]:
                notes.append("默认负责人休息，任务已转派")
    return {"required": required, "recommended": [], "optional": [], "notes": notes}
```

Then expand `scheduler.py` to evaluate day-state, rest-day policy, `priority_score`, `fit_score`, and plan bucket assignment.

**Step 4: Run test to verify it passes**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_scheduler.py -q
```

Expected: the task is reassigned and the note explains why.

**Step 5: Commit**

```bash
git add home-with-me/tests/test_scheduler.py home-with-me/scripts/generate_daily_plan.py home-with-me/scripts/homewithme/scheduler.py home-with-me/scripts/homewithme/events.py
git commit -m "feat: generate home-with-me daily chore plans"
```

### Task 6: Add Snapshot Rebuild Support

**Files:**
- Create: `home-with-me/tests/test_rebuild_snapshot.py`
- Create: `home-with-me/scripts/rebuild_snapshot.py`
- Modify: `home-with-me/scripts/homewithme/events.py`
- Modify: `home-with-me/scripts/homewithme/storage.py`

**Step 1: Write the failing test**

```python
import json

from rebuild_snapshot import rebuild_snapshot
from init_household import build_initial_files
from apply_event import apply_event_payload
from homewithme.storage import default_household_paths


def test_rebuild_snapshot_recreates_current_state_from_events(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    build_initial_files(
        {
            "household": {"name": "Test", "timezone": "Asia/Shanghai"},
            "members": [{"id": "mimi", "display_name": "咪咪"}],
            "tasks": [{"id": "wash-dishes", "name": "洗碗", "default_assignee": "mimi"}],
        }
    )
    apply_event_payload(
        {
            "type": "task_completed",
            "task_id": "wash-dishes",
            "performed_by": "mimi",
            "completed_at": "2026-03-15T09:30:00+08:00",
        }
    )

    paths = default_household_paths()
    paths.state.unlink()

    rebuild_snapshot()

    state = json.loads(paths.state.read_text())
    assert state["tasks"]["wash-dishes"]["last_completed_at"] == "2026-03-15T09:30:00+08:00"
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_rebuild_snapshot.py -q
```

Expected: fail because rebuild logic does not yet exist.

**Step 3: Write minimal implementation**

```python
def rebuild_snapshot() -> dict:
    config = load_config()
    state = build_initial_state(config)
    for event in read_all_events():
        state = reduce_event(state, event)
    save_state(state)
    return state
```

**Step 4: Run test to verify it passes**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_rebuild_snapshot.py -q
```

Expected: deleting `state/current.json` no longer loses household runtime state.

**Step 5: Commit**

```bash
git add home-with-me/tests/test_rebuild_snapshot.py home-with-me/scripts/rebuild_snapshot.py home-with-me/scripts/homewithme/events.py home-with-me/scripts/homewithme/storage.py
git commit -m "feat: rebuild home-with-me snapshots from event logs"
```

### Task 7: Add Natural-Language Routing And Skill Instructions

**Files:**
- Create: `home-with-me/tests/test_intents.py`
- Create: `home-with-me/scripts/homewithme/intents.py`
- Modify: `home-with-me/SKILL.md`
- Create: `home-with-me/references/schema.md`
- Create: `home-with-me/references/intent-patterns.md`
- Modify: `home-with-me/agents/openai.yaml`

**Step 1: Write the failing test**

```python
from homewithme.intents import classify_intent


def test_classify_completion_update_with_member_alias():
    result = classify_intent("男朋友刚倒了垃圾")

    assert result.intent == "report_completion"
    assert result.task_hint == "倒垃圾"
    assert result.member_hint == "男朋友"
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_intents.py -q
```

Expected: fail because the intent classifier does not exist.

**Step 3: Write minimal implementation**

```python
from dataclasses import dataclass


@dataclass
class IntentMatch:
    intent: str
    member_hint: str | None = None
    task_hint: str | None = None


def classify_intent(text: str) -> IntentMatch:
    if "做什么" in text or "待办" in text:
        return IntentMatch(intent="view_plan")
    if "洗完" in text or "刚倒了" in text:
        return IntentMatch(intent="report_completion", member_hint="男朋友", task_hint="倒垃圾")
    raise ValueError("Ambiguous input")
```

Then refine the implementation to keep the classifier conservative, return structured ambiguity states, and update `SKILL.md` so the language layer always confirms uncertain entity matches before writing state.

**Step 4: Run test to verify it passes**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_intents.py -q
```

Expected: high-frequency natural-language patterns classify correctly.

**Step 5: Validate skill metadata**

Run:

```bash
python /Users/blizhan/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/blizhan/data/code/opencode/home-with-me
```

Expected: `SKILL.md` and `agents/openai.yaml` remain valid after updates.

**Step 6: Commit**

```bash
git add home-with-me/tests/test_intents.py home-with-me/scripts/homewithme/intents.py home-with-me/SKILL.md home-with-me/references/schema.md home-with-me/references/intent-patterns.md home-with-me/agents/openai.yaml
git commit -m "feat: add home-with-me language routing and skill docs"
```

### Task 8: Add End-To-End Planner Output Validation

**Files:**
- Create: `home-with-me/tests/test_end_to_end.py`
- Modify: `home-with-me/scripts/generate_daily_plan.py`
- Modify: `home-with-me/scripts/apply_event.py`
- Modify: `home-with-me/scripts/init_household.py`

**Step 1: Write the failing test**

```python
from init_household import build_initial_files
from generate_daily_plan import render_daily_plan


def test_render_daily_plan_writes_markdown_and_json_outputs(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    build_initial_files(
        {
            "household": {"name": "Home", "timezone": "Asia/Shanghai"},
            "members": [{"id": "mimi", "display_name": "咪咪"}],
            "tasks": [{"id": "wash-dishes", "name": "洗碗", "default_assignee": "mimi"}],
        }
    )

    result = render_daily_plan(target_date="2026-03-15")

    assert result.markdown_path.exists()
    assert result.json_path.exists()
    assert "必做" in result.markdown_path.read_text()
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_end_to_end.py -q
```

Expected: fail because output rendering and file writing are incomplete.

**Step 3: Write minimal implementation**

```python
def render_daily_plan(target_date: str) -> RenderedPlan:
    plan = generate_daily_plan_for_target(target_date)
    markdown_path = write_markdown_plan(plan, target_date)
    json_path = write_json_plan(plan, target_date)
    append_event(..., {"type": "daily_plan_generated", "target_date": target_date})
    return RenderedPlan(markdown_path=markdown_path, json_path=json_path)
```

**Step 4: Run the focused test**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests/test_end_to_end.py -q
```

Expected: planner output files are created and contain the required sections.

**Step 5: Run the full suite**

Run:

```bash
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests -q
```

Expected: all HomeWithMe tests pass.

**Step 6: Commit**

```bash
git add home-with-me/tests home-with-me/scripts/generate_daily_plan.py home-with-me/scripts/apply_event.py home-with-me/scripts/init_household.py
git commit -m "feat: validate home-with-me end-to-end flows"
```

### Task 9: Final Verification And Example Household Smoke Test

**Files:**
- Modify: `home-with-me/references/schema.md`
- Modify: `home-with-me/references/intent-patterns.md`
- Modify: `home-with-me/SKILL.md`

**Step 1: Create a sample household**

Run:

```bash
HOME="$(mktemp -d)" python /Users/blizhan/data/code/opencode/home-with-me/scripts/init_household.py
```

Expected: the script walks through or accepts a fixture household and creates a fresh `.homewithme/` directory tree.

**Step 2: Generate a sample daily plan**

Run:

```bash
HOME="<same-temp-home>" python /Users/blizhan/data/code/opencode/home-with-me/scripts/generate_daily_plan.py --date 2026-03-15
```

Expected: Markdown and JSON plan outputs are created under the temp household directory.

**Step 3: Apply a completion event**

Run:

```bash
HOME="<same-temp-home>" python /Users/blizhan/data/code/opencode/home-with-me/scripts/apply_event.py --type task_completed --task wash-dishes --member mimi
```

Expected: the event log grows and the snapshot updates.

**Step 4: Rebuild the snapshot**

Run:

```bash
HOME="<same-temp-home>" python /Users/blizhan/data/code/opencode/home-with-me/scripts/rebuild_snapshot.py
```

Expected: the rebuilt snapshot matches the pre-rebuild state for the exercised task.

**Step 5: Run validation**

Run:

```bash
python /Users/blizhan/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/blizhan/data/code/opencode/home-with-me
cd /Users/blizhan/data/code/opencode/home-with-me && pytest tests -q
```

Expected: both the skill validator and the test suite pass.

**Step 6: Commit**

```bash
git add home-with-me
git commit -m "docs: finalize home-with-me skill for initial release"
```
