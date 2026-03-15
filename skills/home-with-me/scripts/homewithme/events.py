def reduce_event(state: dict, event: dict) -> dict:
    if event["type"] == "task_completed":
        task = state["tasks"][event["task_id"]]
        task["last_completed_at"] = event["completed_at"]
        task["status"] = "done"
        task["deferred_until"] = None
    elif event["type"] == "task_deferred":
        task = state["tasks"][event["task_id"]]
        task["status"] = "deferred"
        task["deferred_until"] = event["defer_until"]
        task["next_due_at"] = event["defer_until"]
    elif event["type"] == "task_skipped":
        task = state["tasks"][event["task_id"]]
        task["status"] = "skipped"
        task["skip_count"] = task.get("skip_count", 0) + 1
    elif event["type"] == "task_reassigned":
        task = state["tasks"][event["task_id"]]
        task["status"] = "active"
        task["assigned_to"] = event["assignee_id"]
    return state
