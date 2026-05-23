# 第 1 阶段交接说明 v0.1

阶段：典籍与规则调研  
目标：为第 2 阶段“排盘引擎 MVP”提供可追溯、可审校、可编码的资料基础。  
当前状态：v0.1 已完成，可进入第 2 阶段技术设计与黄金样例准备。

## 验收状态

| 验收项 | 状态 | 说明 |
|---|---|---|
| 六本指定典籍均有资料卡 | 已完成 | 见 `data/classic_source_cards.v0.1.md` |
| 术语表覆盖核心概念 | 已完成 | 当前 55 条术语，覆盖日辰、四课、三传、月将、占时、天地盘、十二天将、类神、神煞、课体、空亡、刑冲合害、旺相休囚等 |
| 问题分类表支撑语音代理意图识别 | 已完成 | 当前 16 个分类，含高风险降级类 |
| 规则版本表记录至少 5 类关键差异 | 已完成 | 当前 12 个差异点 |
| 规则/出处卡不少于 100 条 | 已完成 | 当前 112 条 |
| 关键判断区分依据类型 | 已完成 | 每条规则卡含直接依据、现代转述、产品化推论、娱乐表达或安全规则 |
| 不可上线内容清单完成 | 已完成 | 当前 20 条，覆盖版权与高风险决策 |
| 可交给第 2 阶段 | 已完成 | 但排盘规则仍需黄金样例和专家审校 |

## 第 2 阶段优先规则

优先把以下 20 条规则转成排盘引擎和解释器的接口约束：

| 优先级 | 规则卡 | 用途 |
|---|---|---|
| P0 | RC-001 | 定义起课输入字段 |
| P0 | RC-002 | 统一占问时间与时区 |
| P0 | RC-003 | 建立规则版本配置 |
| P0 | RC-004 | 布天地盘输出 |
| P0 | RC-005 | 生成四课 |
| P0 | RC-006 | 生成三传与判定路径 |
| P0 | RC-007 | 布十二天将并记录起法 |
| P0 | RC-008 | 按问题类别选择类神 |
| P0 | RC-009 | 神煞只作辅助信号 |
| P0 | RC-010 | 输出事实/依据/推论/娱乐分层 |
| P0 | RC-045 | 元首课候选条件 |
| P0 | RC-048 | 重审课候选条件 |
| P0 | RC-051 | 九宗目录作为三传规则组 |
| P0 | RC-052 | 九宗命名与别名统一 |
| P0 | RC-055 | rule_trace 记录取传原因 |
| P0 | RC-089 | 语音代理必须通过后端排盘 |
| P0 | RC-091 | 无 chart_json 不得伪造课式 |
| P0 | RC-094 | liuren_rule 数据模型字段 |
| P0 | RC-095 | chart 数据模型字段 |
| P0 | RC-103 | 高风险类别安全降级 |

## 第 2 阶段建议接口字段

`create_liuren_chart` 输入：

```json
{
  "question": "string",
  "datetime": "ISO-8601 string",
  "timezone": "IANA timezone string",
  "location": "string|null",
  "category": "question category id|null",
  "manual_params": {
    "month_general": "string|null",
    "divination_hour": "string|null",
    "year_fate": "string|null",
    "school_version": "string"
  }
}
```

`create_liuren_chart` 输出：

```json
{
  "chart_id": "string",
  "school_version": "string",
  "datetime_normalized": "ISO-8601 string",
  "ganzhi": {
    "day": "string"
  },
  "month_general": "string",
  "earth_plate": [],
  "heaven_plate": [],
  "four_lessons": [],
  "three_transmissions": [],
  "generals": [],
  "shensha": [],
  "rule_trace": {
    "month_general_policy": "string",
    "general_policy": "string",
    "transmission_candidates": [],
    "selected_transmission_rule": "string"
  }
}
```

## 关键风险

- 《大六壬玉藻金英》是现代出版物，未授权前不能录入正文。
- 《大六壬课经》用户指定版本尚未确认，目前只能以“课经传统”和《六壬大全》卷七作为调研线索。
- 三传、贵人昼夜、月将截取、神煞启用范围必须做成配置，不应硬编码成单一正统。
- 第 2 阶段必须先做 20 个黄金样例课，否则无法证明排盘引擎可复现。
- 解释器必须依赖 `chart_json` 和 `evidence_ids`，不得由语言模型自由生成课式或出处。

## 下一步

1. 选定第 2 阶段默认规则版本：先采用 `school_v0_research_default`。
2. 从 `RC-044` 至 `RC-065` 相关课体资料中挑选 20 个黄金样例候选。
3. 设计 `liuren_rule` 与 `chart` JSON schema。
4. 实现最小排盘引擎时，先覆盖时间规整、天地盘、四课、元首/重审等可验证规则。
5. 每个引擎结果都输出 `rule_trace`，供专业版解释和测试断言使用。
