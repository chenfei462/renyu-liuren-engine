# 第 9 阶段交接说明 v0.1

阶段：小范围上线运维与反馈复盘 MVP  
目标：在第 8 阶段发布准备之后，建立上线闸门、运维指标、反馈分流、安全事件和暂停恢复机制。

## 已交付

| 项目 | 文件 | 说明 |
|---|---|---|
| 运维配置 | `data/ops_config.v0.1.json` | 定义 `blocked`、`canary`、`paused` 状态、P0/P1 事件和反馈分流类型 |
| 运维事件 | `data/ops_events.v0.1.jsonl` | 本地 JSONL 记录安全事件、接口失败、Realtime 失败、暂停和恢复 |
| 运维模块 | `src/liuren_engine/ops.py` | 提供状态判断、事件记录、指标聚合、反馈分流和阶段报告 |
| 运维 API | `src/liuren_engine/webapp.py` | 新增 `/api/ops/status`、`/api/ops/metrics`、`/api/ops/feedback/triage`、`/api/ops/event`、`/api/ops/pause`、`/api/ops/resume` |
| 暂停保护 | `src/liuren_engine/webapp.py` | `paused` 状态下 `/api/liuren/interpret` 只返回维护/安全说明 |
| 前端状态 | `static/release/index.html`、`static/realtime/index.html` | 发布首页显示运维状态，Web App 显示暂停公告 |
| Schema | `schemas/` | 新增运维状态、指标、事件、反馈分流和报告 schema |
| 测试 | `tests/test_phase9_ops.py` | 覆盖发布闸门、暂停事件、反馈分流、指标、API、暂停保护和前端契约 |

## 当前上线闸门

默认遵守第 8 阶段发布准入：如果 `/api/release/readiness` 返回 `blocked`，`/api/ops/status` 必须保持 `blocked`，不得进入 `canary`。

当前阻断重点仍是专家审校待处理规则，包括比用、涉害、遥克、昴星、八专、别责、伏吟、返吟等复杂九宗规则。

## 运维状态规则

- `blocked`：发布准入存在阻断项，不开放受邀测试。
- `canary`：发布准入通过，仅开放 20-50 名受邀用户。
- `paused`：出现 P0/P1 事件或手动暂停，解释接口只返回维护/安全说明。

## 反馈复盘

自动进入人工复核的反馈：

- `blocked_reasons` 非空。
- 高风险类别或 `safety_only`。
- `safety_issue`、`source_insufficient`、`chart_question`。

## 下一步

如果状态仍为 `blocked`，下一轮应先处理专家审校和阻断清单。只有状态进入 `canary` 后，才执行 20-50 名用户的小范围真实运维测试。
