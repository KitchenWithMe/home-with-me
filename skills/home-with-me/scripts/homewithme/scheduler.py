from datetime import date


WEEKDAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def generate_daily_plan(config: dict, state: dict, target_date: str) -> dict:
    target = date.fromisoformat(target_date)
    members = {member["id"]: member for member in config.get("members", [])}
    required = []
    notes = []

    for task in config.get("tasks", []):
        runtime = state.get("tasks", {}).get(task["id"], {})
        if runtime.get("status") != "active":
            continue
        if runtime.get("next_due_at") != target_date:
            continue

        default_assignee = members[task["default_assignee"]]
        assignee = default_assignee

        if member_day_state(default_assignee, target) == "rest_day" and task.get("rest_day_policy") == "must_reassign":
            backup_ids = task.get("backup_assignees", [])
            assignee = next((members[member_id] for member_id in backup_ids if member_id in members), default_assignee)
            if assignee["id"] != default_assignee["id"]:
                notes.append(f"{default_assignee['id']} 今天是休息日，{task['name']} 已转派给 {assignee['id']}。")

        required.append(
            {
                "task_id": task["id"],
                "assignee_id": assignee["id"],
                "reason": "due_today",
            }
        )

    return {"required": required, "recommended": [], "optional": [], "notes": notes}


def member_day_state(member: dict, target: date) -> str:
    weekday = WEEKDAY_NAMES[target.weekday()]
    if weekday in member.get("fixed_rest_weekdays", []):
        return "rest_day"
    return "regular_day"
