from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from homewithme.storage import default_household_paths, ensure_household_layout


def test_default_household_paths_point_to_home_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    paths = default_household_paths()

    assert paths.root == tmp_path / ".homewithme"
    assert paths.config == tmp_path / ".homewithme" / "config.yaml"
    assert paths.state == tmp_path / ".homewithme" / "state" / "current.json"


def test_ensure_household_layout_creates_runtime_directories(tmp_path):
    root = tmp_path / ".homewithme"

    ensure_household_layout(root)

    assert (root / "state").is_dir()
    assert (root / "events").is_dir()
    assert (root / "outputs").is_dir()
