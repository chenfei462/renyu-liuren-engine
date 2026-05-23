# 第 11 阶段 Canary 报告 v0.1

## 当前判断

默认建议为 `do_not_publicly_release`。第 11 阶段只提供灰度执行和公开发布准入判断，不直接公开发布。

## 指标口径

- 会话数：`canary_session_log.v0.1.jsonl` 中非 seed 记录数量。
- 回访：同一测试编号出现两次以上 canary 会话。
- 分享：`growth_events.v0.1.jsonl` 中 `share_report_generated`。
- 学习：`learning_card_click`。
- 商业化兴趣：`member_interest`、`course_interest`、`business_interest`，仅作测试复盘。

## 公开发布阻断项

- 专家审校未清障。
- Canary 未运行或样本不足。
- 高风险漏拦截、无出处判断、确定性承诺、版权 blocked 展示、Realtime 工具绕过。
- 用户不能理解安全边界或反馈指出出处不足。
