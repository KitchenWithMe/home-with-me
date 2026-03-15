# HomeWithMe Intent Patterns

## Supported Intent Groups

- `initialize_household`
- `view_plan`
- `report_completion`
- `adjust_schedule`
- `update_rules`

## Common Examples

- `帮我创建一个两人家庭家务系统` -> `initialize_household`
- `今天要做什么` -> `view_plan`
- `生成今天待办` -> `view_plan`
- `我洗完碗了` -> `report_completion`
- `男朋友刚倒了垃圾` -> `report_completion`
- `今天不做拖地，延到周末` -> `adjust_schedule`
- `我周三周五休息，不要给我派任务` -> `update_rules`

## Clarification Rules

Ask a follow-up question before writing state when:

- the member is ambiguous
- the task is ambiguous
- the date or range changes the meaning
- a permanent rule change and a one-off change are both plausible
