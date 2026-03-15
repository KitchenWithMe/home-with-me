import argparse

from homewithme.config_io import read_config
from homewithme.events import reduce_event
from homewithme.storage import default_household_paths, read_all_events, write_state
from init_household import build_initial_state


def rebuild_snapshot() -> dict:
    paths = default_household_paths()
    config = read_config(paths.config)
    state = build_initial_state(config)
    for event in read_all_events(paths.events_dir):
        state = reduce_event(state, event)
    write_state(paths.state, state)
    return state


def main(argv=None) -> dict:
    parser = argparse.ArgumentParser()
    parser.parse_args(argv)
    return rebuild_snapshot()


if __name__ == "__main__":
    main()
