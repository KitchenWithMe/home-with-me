import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

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
