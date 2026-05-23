from __future__ import annotations

from typing import Any


NON_LIUREN_BLOCKED_REASON = "non_liuren_question"
NON_LIUREN_OVERVIEW = "这个输入框只用于具体事项占问，不用于天气、新闻、百科、计算、翻译或闲聊。"
NON_LIUREN_PROMPTS = [
    "可以改写成具体事项，例如：明天出行是否顺利？",
    "也可以问：这个合作能不能推进？这件事适不适合做？",
]

NON_LIUREN_KEYWORDS = (
    "天气",
    "气温",
    "下雨",
    "几点",
    "现在时间",
    "今天几号",
    "新闻",
    "百科",
    "是谁",
    "是什么",
    "怎么算",
    "计算",
    "翻译",
    "讲个笑话",
    "闲聊",
)

LIUREN_INTENT_KEYWORDS = (
    "起课",
    "占问",
    "看看",
    "能不能",
    "是否",
    "适合",
    "顺利",
    "推进",
    "合作",
    "出行",
    "项目",
    "选择",
    "要不要",
    "该不该",
    "可不可以",
)


def is_liuren_question(question: str | None) -> bool:
    text = (question or "").strip()
    if not text:
        return False
    if any(keyword in text for keyword in NON_LIUREN_KEYWORDS):
        return any(keyword in text for keyword in ("是否", "顺利", "适合", "能不能", "要不要", "该不该"))
    return any(keyword in text for keyword in LIUREN_INTENT_KEYWORDS)


def build_non_liuren_response(mode: str, *, include_openrouter: bool = False) -> dict[str, Any]:
    response: dict[str, Any] = {
        "chart": None,
        "evidence": [],
        "interpretation": {
            "mode": mode,
            "overview": NON_LIUREN_OVERVIEW,
            "chart_facts": {},
            "evidence": [],
            "rule_reasoning": [],
            "plain_explanation": [],
            "action_prompts": NON_LIUREN_PROMPTS,
            "blocked_reasons": [NON_LIUREN_BLOCKED_REASON],
            "entertainment": {
                "persona_lines": [],
                "learning_cards": [],
                "share_report": {},
            },
        },
        "safety": {
            "action": "input_only",
            "is_high_risk": False,
            "risk_type": NON_LIUREN_BLOCKED_REASON,
        },
    }
    if include_openrouter:
        response["openrouter"] = {
            "status": "skipped",
            "model": "",
            "content": "",
            "usage": {},
        }
    return response
