# 第 7 阶段交接说明 v0.1

阶段：受限 Beta 测试 MVP  
目标：在第 6 阶段安全准入约束下，开放小范围、可观测、可收集反馈的本地 Beta 原型。

## 已交付

| 项目 | 文件 | 说明 |
|---|---|---|
| Beta 范围配置 | `data/beta_config.v0.1.json` | 明确允许模式、允许占类、禁止占类、反馈类型、退出条件和 Beta 文案 |
| 反馈记录 | `data/beta_feedback.v0.1.jsonl` | 本地 JSONL，默认不保存录音或密钥类字段 |
| Beta 报告种子 | `data/beta_test_report.v0.1.json` | 初始报告文件，运行时由 API 动态聚合反馈 |
| Beta 模块 | `src/liuren_engine/beta.py` | 提供配置加载、Beta 范围判断、反馈写入、报告聚合 |
| 解释器扩展 | `src/liuren_engine/interpreter.py` | 新增 `beta_scope`、`feedback_token`、`tester_notice` |
| API 扩展 | `src/liuren_engine/webapp.py` | 新增 `/api/beta/config`、`/api/beta/feedback`、`/api/beta/report` |
| Realtime 约束 | `src/liuren_engine/realtime.py` | 开场提示加入受限 Beta 与传统文化学习/娱乐边界 |
| 前端原型 | `static/realtime/` | 增加 Beta 标识、测试编号、反馈面板、安全状态展示 |
| Schema | `schemas/` | 新增 Beta 配置、反馈、报告 schema |
| 测试 | `tests/test_phase7_beta.py` | 覆盖配置、解释输出、反馈、报告、API、Realtime 提示和 schema |

## Beta 范围

允许：

- `professional`、`plain`、`story`、`mentor` 四种已实现模式。
- 学习、娱乐、合作/谋望等低风险文化解释。
- 本地分享报告，但必须包含受限 Beta 与不构成现实建议提示。

继续阻断或降级：

- 医疗健康、法律诉讼、投资金融、人身安全。
- 隐私窥探、感情操控、应期承诺、无出处断语。
- 未经专家审校的复杂九宗完整断法。

## 反馈与观测

反馈字段包含 `tester_id`、`chart_id`、`mode`、`category`、`safety_action`、`blocked_reasons`、`feedback_type`、`note`、`timestamp`。

报告聚合包含会话数、反馈数、模式分布、反馈分布、高风险触发次数、安全拦截次数、语音体验失败次数和人工复核样例。

## 手动验收建议

邀请 10-20 名测试用户，每名用户至少完成：

- 一次专业/白话解释。
- 一次故事/导师模式切换。
- 一次高风险问题降级测试。

重点记录语音连接失败、理解困难、出处不足、安全误触发、安全漏拦截和排盘疑问。

## 下一阶段输入

第 8 阶段应基于 `GET /api/beta/report` 和人工复核清单决定是否进入发布准备。若出现高风险漏拦截、伪造出处、版权 blocked 内容展示或 Realtime 绕过本地工具，应暂停 Beta 并回到第 6 阶段修正。
