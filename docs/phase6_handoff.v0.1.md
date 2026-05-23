# 第 6 阶段交接说明 v0.1

阶段：安全、版权与专家审校 MVP  
目标：在第 2-5 阶段能力之上，建立进入 Beta 前的安全审查、版权边界、专家审校和准入判断机制。

## 已交付

| 项目 | 文件 | 说明 |
|---|---|---|
| 安全策略 | `data/safety_policy.v0.1.json` | 覆盖医疗、法律、投资、人身安全、隐私、操控、确定性预测、应期和神煞单独断结论 |
| 红队样例 | `data/red_team_cases.v0.1.json` | 覆盖高风险、隐私、操控关系、绕过安全、伪造出处和模型自行排盘 |
| 专家审校清单 | `data/expert_review_cases.v0.1.json` | 从 100 个 golden cases 展开，并补充九宗、天将角色和安全降级审校项 |
| 版权审查清单 | `data/copyright_review.v0.1.json` | 标记 `approved_for_beta`、`summary_only`、`blocked` |
| 安全校验模块 | `src/liuren_engine/safety_review.py` | 提供 `validate_safety`、`validate_beta_readiness` 和数据加载函数 |
| 解释器集成 | `src/liuren_engine/interpreter.py` | 输出 `safety_validation`、`beta_readiness_flags`、`blocked_reasons` |
| API | `src/liuren_engine/webapp.py` | 新增 `/api/safety/policy`、`/api/safety/validate`、`/api/review/status` |
| Realtime 约束 | `src/liuren_engine/realtime.py` | 播报前要求检查 `safety_validation` 与 `blocked_reasons` |
| Schema | `schemas/` | 新增第 6 阶段安全校验和审校状态接口契约 |
| 测试 | `tests/test_phase6_safety_review.py` | 覆盖安全策略、红队、版权、专家审校、解释器字段和 API |

## 安全规则

- 高风险类别：医疗、法律、投资、人身安全必须返回 `safety_only`。
- 禁止输出确定性承诺、胜率、收益、诊断、用药、胜诉等表达。
- 神煞只能作为辅助标签，不得单独形成结论。
- 无 `chart_json` 或无出处证据时，专业版不得生成判断。
- Realtime 模型不得自行排盘、不得伪造出处，必须基于工具返回结果。

## Beta 准入结论

当前状态：**不建议直接开放完整 Beta**。

允许进入 Beta 的范围：

- 学习模式。
- 娱乐模式。
- 合作/谋望等低风险问题。
- 有 `chart_json`、出处卡和安全校验通过的解释。

暂不进入 Beta 的范围：

- 医疗诊断、用药、病情判断。
- 法律策略、胜诉预测。
- 投资买卖、收益和时机建议。
- 人身安全处置。
- 应期承诺。
- 隐私窥探和感情操控。
- 未专家审校的复杂九宗规则完整断法。

## 当前阻断项

- 专家审校仍有待确认项，尤其是比用、涉害、遥克、昴星、八专、别责、伏吟、返吟。
- 现代出版物、课程资料、论坛长文正文被标记为 `blocked`，不得进入产品正文。
- 红队测试已本地覆盖，但真实 Realtime 外部模型仍需人工语音验收。

## 下一阶段建议

第 7 阶段 Beta 应只开放学习与娱乐场景，并保留安全降级、出处展示和用户反馈入口。复杂占类、应期和高风险现实建议继续保持关闭。
