import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from apply_event import main as apply_event_main
from homewithme.config_io import read_config
from generate_daily_plan import main as generate_daily_plan_main
from init_household import main as init_household_main
from rebuild_snapshot import main as rebuild_snapshot_main


def test_cli_commands_create_and_update_household(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    fixture = tmp_path / "example-household.json"
    fixture.write_text(
        json.dumps(
            {
                "household": {"name": "CLI Home", "timezone": "Asia/Shanghai"},
                "members": [{"id": "mimi", "display_name": "咪咪"}],
                "tasks": [{"id": "wash-dishes", "name": "洗碗", "default_assignee": "mimi"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    init_household_main(["--from-file", str(fixture)])
    generate_daily_plan_main(["--date", "2026-03-15"])
    apply_event_main(
        [
            "--type",
            "task_completed",
            "--task",
            "wash-dishes",
            "--member",
            "mimi",
            "--completed-at",
            "2026-03-15T09:30:00+08:00",
        ]
    )
    rebuild_snapshot_main([])

    root = tmp_path / ".homewithme"
    assert (root / "config.yaml").exists()
    assert (root / "outputs" / "2026-03-15-plan.md").exists()
    assert (root / "state" / "current.json").exists()


def test_init_household_can_bootstrap_from_bundled_example(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    init_household_main(["--example", "starter"])

    root = tmp_path / ".homewithme"
    assert (root / "config.yaml").exists()


def test_bundled_example_uses_photo_based_default_tasks(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    init_household_main(["--example", "starter"])

    config = read_config((tmp_path / ".homewithme" / "config.yaml"))
    tasks = {task["id"]: task for task in config["tasks"]}

    assert tasks["wash-dishes"]["area"] == "kitchen"
    assert tasks["wash-dishes"]["frequency_label"] == "最常做（1-3天/次）"
    assert tasks["wipe-dining-table"]["frequency_label"] == "次常做（1周2次）"
    assert tasks["mop-floor-deep"]["frequency_label"] == "深度清洁（3-4周/次）"
    assert tasks["declutter-inventory"]["frequency_label"] == "盘点维护（季度/次）"
