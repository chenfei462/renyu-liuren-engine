# 第 5 阶段交接说明 v0.1

阶段：娱乐化玩法 MVP  
目标：在排盘引擎、知识库解释器和 Realtime 原型之上，增加十二天将角色化、故事版、导师版学习解释和本地分享报告。

## 已交付

| 项目 | 文件 | 说明 |
|---|---|---|
| 十二天将角色数据 | `data/general_personas.v0.1.json` | 覆盖全部 12 个天将，包含角色名、语气、象意、安全边界和来源 ID |
| 学习卡数据 | `data/learning_cards.v0.1.json` | 覆盖三传、四课、天将、安全边界和重点天将学习卡 |
| 娱乐化逻辑 | `src/liuren_engine/entertainment.py` | 提供角色台词、故事场景、导师步骤、学习卡推荐和本地分享报告 |
| 解释器模式 | `src/liuren_engine/interpreter.py` | `mode` 扩展为 `professional`、`plain`、`story`、`mentor` |
| API | `src/liuren_engine/webapp.py` | 新增 `/api/personas`、`/api/learning/cards`、`/api/report/share` |
| Realtime 工具 | `src/liuren_engine/realtime.py` | 工具 schema 支持 story/mentor，系统指令锁定娱乐与学习边界 |
| Web 原型页 | `static/realtime/` | 增加模式选择、天将角色卡、学习卡和分享报告区域 |
| Schema | `schemas/` | 更新解释器和工具 schema，新增 personas、learning cards、share report schema |
| 测试 | `tests/test_entertainment_phase5.py` | 覆盖角色数据、故事版、导师版、高风险降级、分享报告和 API |

## 新增接口

- `GET /api/personas`
  返回十二天将角色配置，供前端展示角色卡。

- `GET /api/learning/cards`
  返回本地学习卡配置，供学习面板和导师版推荐使用。

- `POST /api/report/share`
  输入 `chart` 和 `interpretation`，输出 `local_share_report`，包含可复制文本和本地 HTML。该接口不生成云端链接，不写数据库。

- `POST /api/liuren/interpret`
  `mode` 支持：
  - `professional`：专业版，保留出处和规则路径。
  - `plain`：白话版，降低术语密度。
  - `story`：故事版，生成角色化表达。
  - `mentor`：导师版，生成规则路径学习步骤。

## 安全边界

- 故事版只改变表达方式，不改变排盘事实、证据或规则判断。
- 导师版只解释 `chart_json.rule_trace` 中已经存在的路径，不重新计算课式。
- 医疗、法律、投资、人身安全分类继续强制 `safety_only`，不输出角色对白或现实建议。
- 分享报告标注为传统文化学习与娱乐体验，不作为现实决策依据。

## 验收状态

- 十二天将角色数据覆盖 12/12。
- 故事版包含娱乐标记和出处保留。
- 导师版能解释元首/重审等已实现规则路径。
- 100 个 golden cases 的专业版覆盖率保持 `evidence_coverage_ratio >= 0.8`。
- 前端静态契约包含四种模式、角色卡、学习卡和分享报告。

## 当前限制

- 分享报告仅本地生成，不提供永久链接、二维码、图片导出或 PDF 导出。
- 角色化只做文字人设，不包含插画、动画、专属音色或角色语音。
- 浏览器只保存当前会话中的最近一次工具结果，刷新后不保留上下文。
