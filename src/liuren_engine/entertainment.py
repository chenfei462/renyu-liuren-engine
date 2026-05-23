from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


GENERAL_PERSONAS_PATH = Path("data") / "general_personas.v0.1.json"
LEARNING_CARDS_PATH = Path("data") / "learning_cards.v0.1.json"
ENTERTAINMENT_LABEL = "文化娱乐/学习体验"


def _project_root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def load_general_personas(root: str | Path | None = None) -> list[dict]:
    path = _project_root(root) / GENERAL_PERSONAS_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def load_learning_cards(root: str | Path | None = None) -> list[dict]:
    path = _project_root(root) / LEARNING_CARDS_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def _selected_lesson_type(chart_json: Mapping[str, Any]) -> str:
    transmissions = chart_json.get("three_transmissions", [])
    if not transmissions:
        return "未识别课体"
    return str(transmissions[0].get("lesson_type", "未识别课体"))


def _active_general_names(chart_json: Mapping[str, Any]) -> list[str]:
    available = [str(item.get("general")) for item in chart_json.get("generals", []) if item.get("general")]
    symbols = [str(item) for item in chart_json.get("rule_trace", {}).get("category_symbols", [])]
    selected = [name for name in symbols if name in available]
    if not selected:
        selected = available[:4]
    for name in available:
        if len(selected) >= 4:
            break
        if name not in selected:
            selected.append(name)
    return selected[:4]


def _branch_for_general(chart_json: Mapping[str, Any], general: str) -> str:
    for item in chart_json.get("generals", []):
        if item.get("general") == general:
            return str(item.get("earth_branch", ""))
    return ""


def persona_lines(chart_json: Mapping[str, Any], personas: Sequence[Mapping[str, Any]] | None = None) -> list[dict]:
    persona_by_general = {item["general"]: item for item in (personas or load_general_personas())}
    lines: list[dict] = []
    for general in _active_general_names(chart_json):
        persona = persona_by_general.get(general)
        if not persona:
            continue
        branch = _branch_for_general(chart_json, general)
        lines.append(
            {
                "general": general,
                "role_name": persona["role_name"],
                "earth_branch": branch,
                "line": f"{persona['role_name']}临{branch or '本课'}：{persona['usable_expression']}",
                "source_ids": persona["source_ids"],
                "safety_note": persona["safety_boundaries"],
            }
        )
    return lines


def build_story_scene(chart_json: Mapping[str, Any], lines: Sequence[Mapping[str, Any]]) -> str:
    lesson_type = _selected_lesson_type(chart_json)
    if not lines:
        return f"【{ENTERTAINMENT_LABEL}】本课识别为{lesson_type}，暂以结构事实为主，不生成角色对白。"
    cast = "、".join(str(item["role_name"]) for item in lines[:3])
    return (
        f"【{ENTERTAINMENT_LABEL}】本课识别为{lesson_type}。"
        f"{cast}依次登场，把课式事实转成可观察的沟通、资源与风险提示。"
    )


def mentor_steps(chart_json: Mapping[str, Any]) -> list[dict]:
    transmissions = chart_json.get("three_transmissions", [])
    selected_rule = chart_json.get("rule_trace", {}).get("selected_transmission_rule")
    source_ids = list(dict.fromkeys(source_id for item in transmissions for source_id in item.get("source_cards", [])))
    lesson_type = _selected_lesson_type(chart_json)
    return [
        {
            "step": "先看课体与三传",
            "rule_id": selected_rule,
            "source_ids": source_ids,
            "explanation": f"当前三传标记为{lesson_type}，导师版只解释已经写入 rule_trace 的取传路径。",
        },
        {
            "step": "再看四课关系",
            "rule_id": "four_lessons_relation_v0",
            "source_ids": ["RC-013", "RC-014", "RC-015"],
            "explanation": "四课关系用于观察结构入口，不能脱离三传和出处单独定结论。",
        },
        {
            "step": "最后看安全边界",
            "rule_id": "safety_boundary_v0",
            "source_ids": ["RC-102", "RC-103"],
            "explanation": "所有输出都按传统文化学习与娱乐体验处理，高风险问题优先安全降级。",
        },
    ]


def recommend_learning_cards(chart_json: Mapping[str, Any], mode: str = "plain", limit: int = 5) -> list[dict]:
    cards = load_learning_cards()
    tokens = {
        mode,
        str(chart_json.get("rule_trace", {}).get("selected_transmission_rule", "")),
        _selected_lesson_type(chart_json),
    }
    tokens.update(str(item) for item in chart_json.get("rule_trace", {}).get("category_symbols", []))
    if chart_json.get("safety", {}).get("action") == "safety_only":
        tokens.update({"安全", "safety_only", str(chart_json.get("safety", {}).get("risk_type", ""))})

    scored: list[tuple[int, dict]] = []
    for card in cards:
        tags = {str(tag) for tag in card.get("tags", [])}
        score = len(tokens & tags)
        if score:
            scored.append((score, card))
    selected = [card for _, card in sorted(scored, key=lambda item: (-item[0], item[1]["card_id"]))]
    if len(selected) < 3:
        for card in cards:
            if card not in selected:
                selected.append(card)
            if len(selected) >= 3:
                break
    return selected[: max(3, min(limit, 5))]


def empty_entertainment_payload(chart_json: Mapping[str, Any]) -> dict:
    return {
        "label": ENTERTAINMENT_LABEL,
        "persona_lines": [],
        "story_scene": "",
        "mentor_steps": [],
        "learning_cards": recommend_learning_cards(chart_json, mode="safety", limit=3),
        "share_report": {},
    }


def build_entertainment_payload(chart_json: Mapping[str, Any], mode: str) -> dict:
    if chart_json.get("safety", {}).get("action") == "safety_only":
        return empty_entertainment_payload(chart_json)
    lines = persona_lines(chart_json)
    payload = {
        "label": ENTERTAINMENT_LABEL,
        "persona_lines": lines,
        "story_scene": build_story_scene(chart_json, lines) if mode == "story" else "",
        "mentor_steps": mentor_steps(chart_json) if mode == "mentor" else [],
        "learning_cards": recommend_learning_cards(chart_json, mode=mode),
        "share_report": {},
    }
    return payload


def _share_report_content_state(interpretation: Mapping[str, Any], safety: Mapping[str, Any]) -> str:
    action = str(
        (interpretation.get("safety_validation") or {}).get("action")
        or safety.get("action")
        or "allow_cultural_interpretation"
    )
    if action == "safety_only":
        return "safety_only"
    if action == "blocked":
        return "blocked"
    return "full_interpretation"


def _share_report_sections(
    interpretation: Mapping[str, Any],
    chart_facts: Mapping[str, Any],
    entertainment: Mapping[str, Any],
    safety: Mapping[str, Any],
) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = [
        {
            "section_id": "overview",
            "title": "Overview",
            "kind": "text",
            "content": str(interpretation.get("overview", "")),
        },
        {
            "section_id": "chart_facts",
            "title": "Chart Facts",
            "kind": "object",
            "content": dict(chart_facts),
        },
    ]
    if entertainment.get("story_scene"):
        sections.append(
            {
                "section_id": "story_scene",
                "title": "Story Scene",
                "kind": "text",
                "content": str(entertainment.get("story_scene", "")),
            }
        )
    if entertainment.get("persona_lines"):
        sections.append(
            {
                "section_id": "persona_lines",
                "title": "Persona Lines",
                "kind": "list",
                "content": list(entertainment.get("persona_lines", [])),
            }
        )
    if entertainment.get("mentor_steps"):
        sections.append(
            {
                "section_id": "mentor_steps",
                "title": "Mentor Steps",
                "kind": "list",
                "content": list(entertainment.get("mentor_steps", [])),
            }
        )
    if entertainment.get("learning_cards"):
        sections.append(
            {
                "section_id": "learning_cards",
                "title": "Learning Cards",
                "kind": "list",
                "content": list(entertainment.get("learning_cards", [])),
            }
        )
    sections.append(
        {
            "section_id": "safety",
            "title": "Safety",
            "kind": "text",
            "content": str(safety.get("disclaimer", "")),
        }
    )
    return sections


def build_share_report(chart_json: Mapping[str, Any], interpretation: Mapping[str, Any]) -> dict:
    chart_id = str(chart_json.get("chart_id", ""))
    lesson_type = _selected_lesson_type(chart_json)
    safety = chart_json.get("safety", {})
    entertainment = interpretation.get("entertainment", {})
    chart_facts = dict(interpretation.get("chart_facts", {}))
    question_focus = interpretation.get("question_focus", {})
    display_question = question_focus.get("display_question")
    safe_question_focus = {
        "display_question": str(display_question or ""),
        "focus_terms": list(question_focus.get("focus_terms", [])),
    }
    if display_question:
        chart_facts["question"] = display_question
    text_lines = [
        "壬语本地分享报告",
        f"报告类型：{ENTERTAINMENT_LABEL}",
        f"课 ID：{chart_id}",
        f"课体：{lesson_type}",
        f"摘要：{interpretation.get('overview', '')}",
        f"安全提示：{safety.get('disclaimer', '')}",
        "受限 Beta，不构成现实建议；仅作传统文化学习与娱乐体验。",
    ]
    if entertainment.get("story_scene"):
        text_lines.append(f"故事场景：{entertainment['story_scene']}")
    for line in entertainment.get("persona_lines", [])[:4]:
        text_lines.append(f"{line.get('general')}：{line.get('line')}")

    text = "\n".join(text_lines)
    escaped = html.escape(text).replace("\n", "<br />\n")
    html_document = f"<article data-chart-id=\"{html.escape(chart_id)}\"><p>{escaped}</p></article>"
    sections = _share_report_sections(interpretation, chart_facts, entertainment, safety)
    pdf_report_draft = {
        "format": "pdf_draft",
        "chart_id": chart_id,
        "title": "RenYu local PDF report draft",
        "sections": [
            {"title": "Overview", "content": str(interpretation.get("overview", ""))},
            {"title": "Chart Facts", "content": json.dumps(chart_facts, ensure_ascii=False, sort_keys=True)},
            {"title": "Evidence", "content": json.dumps(interpretation.get("evidence", []), ensure_ascii=False, sort_keys=True)},
            {"title": "Safety", "content": str(safety.get("disclaimer", ""))},
        ],
        "html": html_document,
        "print_css": "body{font-family:serif;line-height:1.6} article{max-width:760px;margin:auto}",
        "storage": "local_only",
        "disclaimer": "traditional culture learning and entertainment experience, not real-world advice",
    }
    content_state = _share_report_content_state(interpretation, safety)
    tracking = {
        "generated_event_type": "share_report_generated",
        "user_reach_event_type": "share_report_user_reached",
        "legacy_count_field": "share_report_count",
        "legacy_count_semantics": "generated_count",
        "user_reach_tracking_status": "pending_frontend_instrumentation",
    }
    return {
        "report_type": "local_share_report",
        "chart_id": chart_id,
        "mode": interpretation.get("mode"),
        "title": "RenYu local share report",
        "summary": str(interpretation.get("overview", "")),
        "question": str(chart_facts.get("question", "")),
        "lesson_type": lesson_type,
        "content_state": content_state,
        "gating": {
            "action": str((interpretation.get("safety_validation") or {}).get("action") or safety.get("action") or ""),
            "blocked_reasons": list(interpretation.get("blocked_reasons") or []),
            "beta_scope": dict(interpretation.get("beta_scope") or {}),
            "beta_readiness_flags": list(interpretation.get("beta_readiness_flags") or []),
        },
        "content": {
            "overview": str(interpretation.get("overview", "")),
            "chart_facts": chart_facts,
            "question_focus": safe_question_focus,
            "evidence_count": len(interpretation.get("evidence", [])),
            "safety_notice": dict(safety),
            "safety_validation": dict(interpretation.get("safety_validation") or {}),
            "story_scene": str(entertainment.get("story_scene", "")),
            "persona_lines": list(entertainment.get("persona_lines", [])),
            "mentor_steps": list(entertainment.get("mentor_steps", [])),
            "learning_cards": list(entertainment.get("learning_cards", [])),
        },
        "sections": sections,
        "text": text,
        "html": html_document,
        "pdf_report_draft": pdf_report_draft,
        "artifacts": {
            "text": {"format": "plain_text", "content": text},
            "html": {"format": "html_fragment", "content": html_document},
            "pdf_report_draft": pdf_report_draft,
        },
        "share_channels": [
            {"channel": "copy_text", "artifact": "text", "ready": bool(text)},
            {"channel": "copy_html", "artifact": "html", "ready": bool(html_document)},
            {"channel": "pdf_draft", "artifact": "pdf_report_draft", "ready": True},
        ],
        "tracking": tracking,
        "storage": "local_only",
    }
