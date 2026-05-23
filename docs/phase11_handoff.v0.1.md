# 第 11 阶段交接包 v0.1

## 范围

本阶段新增受控 Canary 灰度执行层和公开发布准入闸门。默认不绕过第 10 阶段专家审校；如果 `/api/ops/status` 不是 `canary`，会话记录接口只返回阻断说明。

## 新增能力

- `canary_run_config.v0.1.json`：定义 20-50 人灰度范围、测试任务、允许模式和公开发布阈值。
- `canary_session_log.v0.1.jsonl`：记录灰度会话结果，不保存录音、密钥或敏感原文。
- `canary_metrics.v0.1`：聚合会话、回访、模式使用、学习卡、分享、反馈和商业化兴趣。
- `public_release_gate.v0.1`：综合专家审校、安全、版权、Realtime 绕过、出处与 Canary 指标判断是否进入第 12 阶段。

## API

- `GET /api/canary/run/config`
- `POST /api/canary/session`
- `GET /api/canary/metrics`
- `GET /api/public-release/gate`
- `GET /api/phase11/report`

## 默认状态

默认状态仍可能是 `blocked`，原因通常是 `expert_review_pending` 或 canary 样本不足。只有专家审校闸门已开、20-50 人灰度指标达标、无高风险漏拦截和无版权/出处阻断项时，公开发布闸门才会返回 `ready_for_phase12`。

## 手动验收

1. 使用 3 个有效测试编号和 1 个无效编号验证准入。
2. 至少模拟一次高风险问题和一次 Realtime 失败。
3. 检查分享报告、故事版、导师版和运营文案没有确定性承诺。
4. 汇总 `phase11_canary_report.v0.1` 后决定进入第 12 阶段或回到审校/体验修复。
