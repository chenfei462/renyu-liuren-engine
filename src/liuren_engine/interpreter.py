from __future__ import annotations

from typing import Any, Mapping, Sequence

from .beta import beta_block_flags, beta_scope_for, make_feedback_token, tester_notice
from .entertainment import build_entertainment_payload, build_share_report
from .safety_review import beta_readiness_flags, blocked_question_reasons, validate_safety


FORBIDDEN_DETERMINISTIC_WORDS = ["必然", "一定", "保证", "准确率"]
INTERPRETATION_MODES = {"professional", "plain", "story", "mentor"}
UNSAFE_QUESTION_TERMS = ["包赢", "必赚", "确诊", "用药", "胜诉", "必成", "稳赚"]


def _evidence_ids(evidence_cards: Sequence[Mapping[str, Any]]) -> set[str]:
    return {str(card.get("source_id")) for card in evidence_cards if card.get("source_id")}


def _selected_lesson_type(chart_json: Mapping[str, Any]) -> str:
    transmissions = chart_json.get("three_transmissions", [])
    if not transmissions:
        return "未识别课体"
    return str(transmissions[0].get("lesson_type", "未识别课体"))


def assess_evidence_coverage(chart_json: Mapping[str, Any], evidence_cards: Sequence[Mapping[str, Any]]) -> dict:
    if not evidence_cards:
        return {"covered_judgments": 0, "total_judgments": 0, "ratio": 0, "missing_reasons": ["no_evidence_cards"]}

    ids = _evidence_ids(evidence_cards)
    judgments = [
        ("三传/课体", bool(chart_json.get("three_transmissions")) and any(item.get("source_cards") or item.get("needs_expert_review") for item in chart_json["three_transmissions"])),
        ("四课关系", bool(chart_json.get("four_lessons")) and all(item.get("source_rule") for item in chart_json["four_lessons"])),
        ("类神/问题分类", bool(chart_json.get("rule_trace", {}).get("category_symbols") or chart_json.get("category"))),
        ("天将语义", "RC-067" in ids or bool(chart_json.get("generals"))),
        ("神煞辅助", bool(chart_json.get("shensha")) and ("RC-009" in ids or any(item.get("source_cards") for item in chart_json.get("shensha", [])))),
        ("安全降级", bool(chart_json.get("safety")) and ("RC-102" in ids or "RC-103" in ids)),
    ]
    covered = sum(1 for _, ok in judgments if ok)
    total = len(judgments)
    return {
        "covered_judgments": covered,
        "total_judgments": total,
        "ratio": round(covered / total, 3),
        "missing_reasons": [name for name, ok in judgments if not ok],
    }


def _chart_facts(chart_json: Mapping[str, Any]) -> dict:
    transmissions = chart_json.get("three_transmissions", [])
    return {
        "chart_id": chart_json.get("chart_id"),
        "question": chart_json.get("question"),
        "datetime_normalized": chart_json.get("datetime_normalized"),
        "ganzhi": chart_json.get("ganzhi"),
        "month_general": chart_json.get("month_general"),
        "four_lessons": chart_json.get("four_lessons", []),
        "three_transmissions": transmissions,
        "selected_transmission_rule": chart_json.get("rule_trace", {}).get("selected_transmission_rule"),
        "generals": chart_json.get("generals", []),
        "shensha": chart_json.get("shensha", []),
    }


def _question_focus(chart_json: Mapping[str, Any]) -> dict:
    question = str(chart_json.get("question") or "").strip()
    safety = chart_json.get("safety", {})
    unsafe_to_echo = (
        safety.get("action") == "safety_only"
        or bool(blocked_question_reasons(question))
        or any(term in question for term in FORBIDDEN_DETERMINISTIC_WORDS + UNSAFE_QUESTION_TERMS)
    )
    display_question = "当前问题" if unsafe_to_echo else question
    focus_terms = [term for term in ["出行", "合作", "项目", "沟通", "推进", "选择"] if term in display_question]
    return {
        "question": question,
        "display_question": display_question,
        "focus_terms": focus_terms,
    }


def _rule_reasoning(chart_json: Mapping[str, Any], evidence_cards: Sequence[Mapping[str, Any]]) -> list[dict]:
    ids = sorted(_evidence_ids(evidence_cards))
    return [
        {
            "judgment": "课体/三传",
            "rule_id": chart_json.get("rule_trace", {}).get("selected_transmission_rule"),
            "lesson_type": _selected_lesson_type(chart_json),
            "source_ids": [source_id for source_id in ids if source_id.startswith("RC-04") or source_id.startswith("RC-05") or source_id.startswith("RC-06")],
            "needs_expert_review": any(item.get("needs_expert_review") for item in chart_json.get("three_transmissions", [])),
        },
        {
            "judgment": "类神/问题分类",
            "category": chart_json.get("category"),
            "symbols": chart_json.get("rule_trace", {}).get("category_symbols", []),
            "source_ids": [source_id for source_id in ids if source_id in {"RC-008", "RC-016", "RC-020", "RC-021", "RC-022", "RC-023"}],
        },
        {
            "judgment": "神煞辅助",
            "source_ids": [source_id for source_id in ids if source_id in {"RC-009", "RC-030", "RC-037"}],
            "note": "神煞只作为辅助参考，不单独定结论。",
        },
    ]


def _plain_lines(chart_json: Mapping[str, Any]) -> list[str]:
    lesson_type = _selected_lesson_type(chart_json)
    symbols = chart_json.get("rule_trace", {}).get("category_symbols", [])
    question_focus = _question_focus(chart_json)
    lines = [
        f"针对「{question_focus['display_question']}」，本课先看作{lesson_type}结构，用来观察这件事的起点、推进和收束。",
        "四课、三传和天将只作为传统文化里的观察框架，不替代现实判断。",
    ]
    if question_focus["focus_terms"]:
        lines.append("本次问题焦点是：" + "、".join(question_focus["focus_terms"]) + "。")
    if symbols:
        lines.append("本次问题会重点参考：" + "、".join(symbols[:4]) + "。")
    lines.append("适合记录沟通、资源、阻力和下一步可验证的小行动。")
    return lines


def _action_prompts(chart_json: Mapping[str, Any]) -> list[str]:
    safety = chart_json.get("safety", {})
    if safety.get("is_high_risk"):
        risk = safety.get("risk_type") or "高风险事项"
        return [
            f"这是{risk}问题，请优先咨询具备资质的专业人士。",
            "把本次内容只当作传统文化提示，不作为现实决策依据。",
            "整理事实、证据、预算、时间线和可求助对象，再做现实行动。",
        ]
    return [
        "列出当前最需要确认的一条事实。",
        "把沟通对象、责任边界和可观察信号写下来。",
        "一周后复盘现实反馈，不把本次解释当成确定结论。",
    ]


def _attach_beta_metadata(payload: dict, chart_json: Mapping[str, Any], safety_report: Mapping[str, Any], mode: str) -> None:
    scope = beta_scope_for(chart_json, safety_report, mode)
    payload["beta_scope"] = scope
    payload["feedback_token"] = make_feedback_token(
        str(chart_json.get("chart_id", "")),
        mode,
        str(chart_json.get("category") or chart_json.get("safety", {}).get("category") or ""),
    )
    payload["tester_notice"] = tester_notice()
    payload["beta_readiness_flags"] = list(dict.fromkeys(payload.get("beta_readiness_flags", []) + beta_block_flags(scope)))


def _finalize_payload(payload: dict[str, Any], chart_json: Mapping[str, Any], mode: str) -> dict[str, Any]:
    payload["entertainment"] = build_entertainment_payload(chart_json, mode)
    safety_report = validate_safety(payload, chart_json, mode=mode)
    payload["safety_validation"] = safety_report
    payload["beta_readiness_flags"] = beta_readiness_flags(chart_json, safety_report)
    payload["blocked_reasons"] = safety_report["blocked_reasons"]
    _attach_beta_metadata(payload, chart_json, safety_report, mode)
    payload["entertainment"]["share_report"] = build_share_report(chart_json, payload)
    return payload


def generate_interpretation(
    chart_json: Mapping[str, Any] | None,
    evidence_cards: Sequence[Mapping[str, Any]],
    mode: str = "professional",
) -> dict:
    if not chart_json:
        raise ValueError("chart_json is required")
    if mode not in INTERPRETATION_MODES:
        raise ValueError("mode must be professional, plain, story, or mentor")

    coverage = assess_evidence_coverage(chart_json, evidence_cards)
    safety = chart_json.get("safety", {})
    if not evidence_cards and mode == "professional":
        payload = {
            "mode": mode,
            "overview": "依据不足",
            "chart_facts": _chart_facts(chart_json),
            "evidence": [],
            "rule_reasoning": [],
            "plain_explanation": [],
            "action_prompts": _action_prompts(chart_json),
            "safety_notice": safety,
            "evidence_coverage": coverage,
        }
        return _finalize_payload(payload, chart_json, mode)

    lesson_type = _selected_lesson_type(chart_json)
    question_focus = _question_focus(chart_json)
    overview = f"围绕「{question_focus['display_question']}」，本课识别为{lesson_type}，以下只作传统文化学习与娱乐解释。"
    plain_explanation = [] if safety.get("action") == "safety_only" else _plain_lines(chart_json)
    if mode == "professional":
        reasoning = _rule_reasoning(chart_json, evidence_cards)
    elif mode == "mentor":
        reasoning = [{"judgment": "导师式解释", "note": "按课体、四课关系和安全边界分步说明。"}]
    elif mode == "story":
        reasoning = [{"judgment": "故事版解释", "note": "只改变表达方式，排盘事实仍以 chart_json 为准。"}]
    else:
        reasoning = [{"judgment": "白话解释", "note": "保留出处卡，降低术语密度。"}]

    payload = {
        "mode": mode,
        "question_focus": question_focus,
        "overview": overview,
        "chart_facts": _chart_facts(chart_json),
        "evidence": list(evidence_cards),
        "rule_reasoning": reasoning,
        "plain_explanation": plain_explanation,
        "action_prompts": _action_prompts(chart_json),
        "safety_notice": safety,
        "evidence_coverage": coverage,
    }
    payload = _finalize_payload(payload, chart_json, mode)
    rendered = " ".join(
        str(payload.get(field, ""))
        for field in ["overview", "rule_reasoning", "plain_explanation", "action_prompts", "entertainment"]
    )
    for word in FORBIDDEN_DETERMINISTIC_WORDS:
        if word in rendered:
            raise ValueError(f"deterministic wording is not allowed: {word}")
    return payload
