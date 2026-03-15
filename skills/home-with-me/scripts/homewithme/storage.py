import os
import json
from datetime import datetime
from pathlib import Path

from .models import HouseholdPaths


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


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def read_state(path: Path) -> dict:
    return json.loads(path.read_text())


def append_event(events_dir: Path, event: dict) -> Path:
    events_dir.mkdir(parents=True, exist_ok=True)
    timestamp = event.get("recorded_at") or datetime.now().astimezone().isoformat()
    file_path = events_dir / f"{timestamp[:7]}.jsonl"
    event_with_timestamp = {"recorded_at": timestamp, **event}
    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event_with_timestamp, ensure_ascii=False) + "\n")
    return file_path


def read_all_events(events_dir: Path) -> list[dict]:
    events = []
    if not events_dir.exists():
        return events
    for path in sorted(events_dir.glob("*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    return events
