# 第 3 阶段交接说明 v0.1

阶段：知识库与解释器 MVP  
目标：在第 2 阶段排盘引擎之上，提供本地证据检索、出处卡片、专业版/白话版结构化解释。  
边界：不接前端、不接数据库、不接实时语音、不调用外部 LLM。

## 已交付

| 项目 | 文件 | 说明 |
|---|---|---|
| 本地知识库 | `src/liuren_engine/knowledge.py` | 从第 1 阶段 Markdown 资料构建 source cards，并支持精确召回和关键词检索 |
| 解释器 | `src/liuren_engine/interpreter.py` | 提供 `generate_interpretation(chart_json, evidence_cards, mode)` |
| 解释 CLI | `src/liuren_engine/interpret_cli.py` | 输入 request JSON，输出 chart、evidence、interpretation |
| 知识库种子 | `data/source_cards.v0.1.json` | 从 `phase1_research/data/rule_source_cards.v0.1.md` 生成 |
| 覆盖率报告 | `data/interpretation_coverage.v0.1.json` | 100 个 golden cases 的解释证据覆盖率 |
| Schema | `schemas/` | 新增 evidence 与 interpretation 请求/响应契约 |
| 测试 | `tests/test_knowledge_interpreter.py` | 覆盖知识库转换、证据检索、解释器、安全降级、CLI |

## API 入口

Python 调用：

```python
from liuren_engine import create_liuren_chart, retrieve_evidence, generate_interpretation

chart = create_liuren_chart(request)
evidence = retrieve_evidence(chart, query=request.get("question"), mode="professional")
answer = generate_interpretation(chart, evidence, mode="professional")
```

CLI 调用：

```powershell
$env:PYTHONPATH='D:\Desktop\六壬\src'
python -m liuren_engine.interpret_cli --request .\request.json
```

## 输出结构

解释器输出固定包含：

- `overview`
- `chart_facts`
- `evidence`
- `rule_reasoning`
- `plain_explanation`
- `action_prompts`
- `safety_notice`
- `evidence_coverage`

专业版无 evidence 时返回 `overview = "依据不足"`，不会伪造出处。高风险分类沿用第 2 阶段 `safety.action = "safety_only"`，不输出现实决策建议。

## 验收状态

| 验收项 | 状态 |
|---|---|
| 从第 1 阶段 Markdown 生成结构化 source cards | 已完成 |
| 按 source_cards 精确召回 RC-045、RC-048、RC-051 等规则卡 | 已完成 |
| 按课体、天将、类神、神煞关键词补充召回 | 已完成 |
| 专业版输出事实/依据/推论/安全分层 | 已完成 |
| 白话版避免确定性预测措辞 | 已完成 |
| 100 个 golden cases 专业版覆盖率 >= 0.8 | 已完成，当前最低 1.0 |
| 高风险样例只输出安全降级内容 | 已完成 |

## 当前限制

- 检索是本地轻量关键词/BM25-lite 风格，不是向量库。
- 解释模板是规则模板，不调用 LLM。
- source cards 当前主要来自第 1 阶段规则/出处卡；现代出版物正文仍不入库。
- 覆盖率代表“有出处或规则路径”，不代表专家已确认所有术数公式。

## 第 4 阶段建议

1. 将 `interpret_cli` 的三段输出包装为 Web/API 调用对象。
2. 实时语音层只调用 `create_liuren_chart`、`retrieve_evidence`、`generate_interpretation`，不得绕过引擎生成课式。
3. 语音回答优先使用 `overview`、`plain_explanation`、`action_prompts`，专业展开时再读取 `chart_facts` 和 `evidence`。
4. 接入语音前继续补专家审校样例，尤其是比用、涉害、遥克、昴星、八专、别责。
