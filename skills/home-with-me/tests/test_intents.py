from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from homewithme.intents import classify_intent


def test_classify_completion_update_with_member_alias():
    result = classify_intent("男朋友刚倒了垃圾")

    assert result.intent == "report_completion"
    assert result.task_hint == "倒垃圾"
    assert result.member_hint == "男朋友"
