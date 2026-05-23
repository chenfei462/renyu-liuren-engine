# 第 2 阶段交接说明 v0.1

阶段：排盘引擎 MVP  
目标：提供可测试、可追溯、可被后续语音代理调用的 Python 排盘核心包。  
默认规则版本：`school_v0_research_default`

## 已交付

| 项目 | 文件 | 说明 |
|---|---|---|
| Python 核心包 | `src/liuren_engine/` | 提供 `create_liuren_chart(request) -> chart_json` |
| CLI 调试入口 | `src/liuren_engine/cli.py` | 可用 `python -m liuren_engine.cli --request <json>` 输出排盘 JSON |
| 请求/响应 schema | `schemas/` | 锁定后续 API 包装层的输入输出契约 |
| 100 个回归样例 | `data/golden_cases.v0.1.json` | 覆盖元首、重审、伏吟、返吟、待审规则和高风险分类 |
| 测试 | `tests/test_engine_contract.py` | 使用标准库 `unittest`，无第三方依赖 |

## 能力边界

- 已实现：时间规整、手动占时/月将/日干支覆盖、干支日默认算法、天地盘、四课、生克关系、元首/重审、九宗候选轨迹、十二天将、基础神煞、安全降级和 `rule_trace`。
- 已框架化但需专家审校：比用、涉害、遥克、昴星、八专、别责、伏吟、返吟的完整传统公式。
- 不包含：Web API、前端、实时语音、RAG 检索、专业/白话解释器、故事版表达、数据库。

## API 入口

Python 调用：

```python
from liuren_engine import create_liuren_chart

chart = create_liuren_chart({
    "question": "合作项目能不能推进？",
    "datetime": "2026-04-30T10:30:00",
    "timezone": "Asia/Shanghai",
    "category": "Q-001",
    "manual_params": {
        "month_general": "子",
        "divination_hour": "卯",
        "ganzhi_day": "甲子",
        "school_version": "school_v0_research_default"
    }
})
```

CLI 调用：

```powershell
$env:PYTHONPATH='D:\Desktop\六壬\src'
python -m liuren_engine.cli --request .\request.json
```

## 验收状态

- 100 个回归样例均通过。
- 每个输出都包含 `rule_trace.month_general_policy`、`rule_trace.general_policy`、`rule_trace.transmission_candidates`、`rule_trace.selected_transmission_rule`。
- 医疗、法律、投资、人身安全分类输出 `safety.action = "safety_only"`。
- 未专家确认的公式不会伪装成最终定论，输出中保留 `needs_expert_review` 或 `requires_expert_review`。

## 第 3 阶段建议

1. 把 `chart_json` 作为知识库/解释器的唯一排盘事实输入。
2. 用 `rule_trace.selected_transmission_rule` 和 `source_cards` 检索第 1 阶段出处卡。
3. 专业版解释必须展示“课式事实、规则依据、推论、娱乐表达”分层。
4. 在接入语音前，先补专家审校样例，尤其是比用、涉害、遥克、昴星、八专、别责。
