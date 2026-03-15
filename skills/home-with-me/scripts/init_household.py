import argparse
import json
from pathlib import Path
from typing import Optional

from homewithme.config_io import write_config
from homewithme.storage import append_event, default_household_paths, ensure_household_layout, write_state


def build_initial_files(payload: dict) -> None:
    paths = default_household_paths()
    ensure_household_layout(paths.root)
    write_config(paths.config, payload)
    write_state(paths.state, build_initial_state(payload))
    append_event(paths.events_dir, {"type": "config_initialized", "payload": payload})


def build_initial_state(payload: dict) -> dict:
    tasks = {}
    for task in payload.get("tasks", []):
        tasks[task["id"]] = {
            "status": "active",
            "last_completed_at": None,
            "next_due_at": None,
            "deferred_until": None,
            "skip_count": 0,
        }

    return {
        "snapshot_version": 1,
        "tasks": tasks,
        "members": {member["id"]: {"recent_load": 0} for member in payload.get("members", [])},
        "latest_plan": None,
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-file")
    parser.add_argument("--example", choices=["starter"])
    args = parser.parse_args(argv)

    payload_path = resolve_payload_path(args.from_file, args.example)
    with payload_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    build_initial_files(payload)


def resolve_payload_path(from_file: Optional[str], example: Optional[str]) -> Path:
    if from_file:
        return Path(from_file)
    if example == "starter":
        return Path(__file__).resolve().parents[1] / "assets" / "example-household.json"
    raise SystemExit("Either --from-file or --example starter is required.")


if __name__ == "__main__":
    main()
