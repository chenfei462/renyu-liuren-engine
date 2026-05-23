# 第 10 阶段交接包 v0.1

## 范围

本阶段新增专家审校清障、受邀 canary 准入、内容日历和增长事件记录。默认不绕过第 9 阶段发布闸门；复杂九宗审校任务仍未清障时，系统保持 blocked。

## 新增能力

- `expert_review_workflow.v0.1.json`：把比用、涉害、遥克、昴星、八专、别责、伏吟、返吟转为可记录任务。
- `canary_testers.v0.1.json`：本地测试编号和邀请码准入，不引入账号系统。
- `content_calendar.v0.1.json`：本地运营栏目草案，只保存标题、摘要、学习卡和出处卡关联。
- `growth_events.v0.1.jsonl`：记录学习卡点击、分享报告、反馈、课程或会员兴趣等轻量事件，过滤录音、密钥和敏感原文。

## API

- `GET /api/expert/review/tasks`
- `POST /api/expert/review/update`
- `GET /api/canary/config`
- `POST /api/canary/validate`
- `GET /api/content/calendar`
- `GET /api/growth/metrics`
- `POST /api/growth/event`
- `GET /api/growth/report`

## Canary 闸门

`/api/ops/status` 新增 `canary_gate`。当 release readiness 仅因 `expert_review_pending` 阻断，并且所有关键审校任务均为 `approved_for_canary` 或 `research_only` 且 `allow_canary=true` 时，状态可进入 `canary`。

进入 canary 后，`/api/liuren/interpret` 会校验 `tester_id` 或 `invite_code`。未通过时只返回准入说明和安全边界，不进入正常解释链路。

## 仍需人工处理

- 录入至少 8 条复杂九宗规则的专家意见。
- 对 `research_only` 任务确认只显示研究标签，不参与用户判断。
- 用 3 个有效测试编号和 1 个无效编号完成手动准入验收。
