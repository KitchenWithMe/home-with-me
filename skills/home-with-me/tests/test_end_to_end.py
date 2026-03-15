from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from generate_daily_plan import render_daily_plan
from init_household import build_initial_files


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
