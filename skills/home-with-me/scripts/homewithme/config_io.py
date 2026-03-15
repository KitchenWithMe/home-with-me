import json
from pathlib import Path


def read_config(path: Path) -> dict:
    return json.loads(path.read_text())


def write_config(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def update_member(path: Path, member_id: str, updates: dict) -> dict:
    config = read_config(path)
    for member in config.get("members", []):
        if member["id"] == member_id:
            member.update(updates)
            break
    write_config(path, config)
    return config
