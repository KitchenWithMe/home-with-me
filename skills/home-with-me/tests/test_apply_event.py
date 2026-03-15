import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from apply_event import apply_event_payload
from homewithme.storage import default_household_paths
from init_household import build_initial_files


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

    events = list(paths.events_dir.glob("*.jsonl"))
    assert any("task_completed" in path.read_text() for path in events)
