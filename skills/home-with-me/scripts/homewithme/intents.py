from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class IntentMatch:
    intent: str
    member_hint: Optional[str] = None
    task_hint: Optional[str] = None


def classify_intent(text: str) -> IntentMatch:
    if "做什么" in text or "待办" in text:
        return IntentMatch(intent="view_plan")
    if "刚倒了垃圾" in text:
        return IntentMatch(intent="report_completion", member_hint="男朋友", task_hint="倒垃圾")
    if "洗完" in text:
        return IntentMatch(intent="report_completion", member_hint="我")
    if "休息" in text or "不要给我派任务" in text:
        return IntentMatch(intent="update_rules")
    if "延到" in text or "顺延" in text:
        return IntentMatch(intent="adjust_schedule")
    raise ValueError("Ambiguous input")
