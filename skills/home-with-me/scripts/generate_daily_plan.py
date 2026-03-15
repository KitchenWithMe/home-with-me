import json
import argparse
from dataclasses import dataclass

from homewithme.config_io import read_config
from homewithme.scheduler import generate_daily_plan
from homewithme.storage import append_event, default_household_paths, read_state


@dataclass(frozen=True)
class RenderedPlan:
    markdown_path: object
    json_path: object


def render_daily_plan(target_date: str) -> RenderedPlan:
    paths = default_household_paths()
    config = read_config(paths.config)
    state = read_state(paths.state)
    plan = generate_daily_plan(config, state, target_date=target_date)

    markdown_path = paths.outputs_dir / f"{target_date}-plan.md"
    json_path = paths.outputs_dir / f"{target_date}-plan.json"
    paths.outputs_dir.mkdir(parents=True, exist_ok=True)

    markdown_path.write_text(render_markdown(plan), encoding="utf-8")
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_event(paths.events_dir, {"type": "daily_plan_generated", "target_date": target_date})
    return RenderedPlan(markdown_path=markdown_path, json_path=json_path)


def render_markdown(plan: dict) -> str:
    sections = ["今天的家务安排", "", "必做"]
    sections.extend(format_items(plan["required"]))
    sections.extend(["", "建议做"])
    sections.extend(format_items(plan["recommended"]))
    sections.extend(["", "可选做"])
    sections.extend(format_items(plan["optional"]))
    sections.extend(["", "说明"])
    sections.extend(plan["notes"] or ["- 今天没有额外说明。"])
    return "\n".join(sections) + "\n"


def format_items(items: list[dict]) -> list[str]:
    if not items:
        return ["- 暂无"]
    return [f"- {item['task_id']}｜负责人：{item['assignee_id']}" for item in items]


def main(argv=None) -> RenderedPlan:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args(argv)
    return render_daily_plan(target_date=args.date)


if __name__ == "__main__":
    main()
