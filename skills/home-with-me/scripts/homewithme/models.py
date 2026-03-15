from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HouseholdPaths:
    root: Path
    config: Path
    state: Path
    events_dir: Path
    outputs_dir: Path
