import argparse

from homewithme.config_io import update_member
from homewithme.events import reduce_event
from homewithme.storage import append_event, default_household_paths, read_state, write_state


def apply_event_payload(event: dict) -> dict:
    paths = default_household_paths()
    state = read_state(paths.state)
    next_state = reduce_event(state, event)
    if event["type"] == "member_availability_updated":
        update_member(
            paths.config,
            event["member_id"],
            {"fixed_rest_weekdays": event.get("fixed_rest_weekdays", [])},
        )
    append_event(paths.events_dir, event)
    write_state(paths.state, next_state)
    return next_state


def main(argv=None) -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True)
    parser.add_argument("--task")
    parser.add_argument("--member")
    parser.add_argument("--completed-at")
    parser.add_argument("--defer-until")
    parser.add_argument("--assignee")
    args = parser.parse_args(argv)

    event = {"type": args.type}
    if args.task:
        event["task_id"] = args.task
    if args.member:
        event["performed_by"] = args.member
        event["member_id"] = args.member
    if args.completed_at:
        event["completed_at"] = args.completed_at
    if args.defer_until:
        event["defer_until"] = args.defer_until
    if args.assignee:
        event["assignee_id"] = args.assignee

    return apply_event_payload(event)


if __name__ == "__main__":
    main()
