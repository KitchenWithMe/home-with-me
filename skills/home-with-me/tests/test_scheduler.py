from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

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
