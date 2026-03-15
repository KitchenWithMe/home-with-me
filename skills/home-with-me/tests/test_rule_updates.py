import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from apply_event import apply_event_payload
from homewithme.config_io import read_config
from homewithme.storage import default_household_paths
from init_household import build_initial_files


def test_task_deferred_updates_snapshot(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    build_initial_files(
        {
            "household": {"name": "Test", "timezone": "Asia/Shanghai"},
            "members": [{"id": "mimi", "display_name": "咪咪"}],
            "tasks": [{"id": "mop-floor", "name": "拖地", "default_assignee": "mimi"}],
        }
    )

    apply_event_payload(
        {
            "type": "task_deferred",
            "task_id": "mop-floor",
            "defer_until": "2026-03-16",
            "reason": "今天不做拖地",
        }
    )

    state = json.loads(default_household_paths().state.read_text())
    assert state["tasks"]["mop-floor"]["status"] == "deferred"
    assert state["tasks"]["mop-floor"]["deferred_until"] == "2026-03-16"


def test_member_availability_update_persists_to_config(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    build_initial_files(
        {
            "household": {"name": "Test", "timezone": "Asia/Shanghai"},
            "members": [{"id": "mimi", "display_name": "咪咪", "fixed_rest_weekdays": []}],
            "tasks": [],
        }
    )

    apply_event_payload(
        {
            "type": "member_availability_updated",
            "member_id": "mimi",
            "fixed_rest_weekdays": ["wednesday", "friday"],
        }
    )

    config = read_config(default_household_paths().config)
    assert config["members"][0]["fixed_rest_weekdays"] == ["wednesday", "friday"]
