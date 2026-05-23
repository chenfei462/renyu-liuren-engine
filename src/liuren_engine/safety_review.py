from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SAFETY_POLICY_PATH = Path("data") / "safety_policy.v0.1.json"
RED_TEAM_CASES_PATH = Path("data") / "red_team_cases.v0.1.json"
EXPERT_REVIEW_CASES_PATH = Path("data") / "expert_review_cases.v0.1.json"
COPYRIGHT_REVIEW_PATH = Path("data") / "copyright_review.v0.1.json"
GOLDEN_CASES_PATH = Path("data") / "golden_cases.v0.1.json"


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _read_json(root: str | Path | None, path: Path) -> Any:
    return json.loads((_root(root) / path).read_text(encoding="utf-8"))


def load_safety_policy(root: str | Path | None = None) -> dict:
    return _read_json(root, SAFETY_POLICY_PATH)


def load_red_team_cases(root: str | Path | None = None) -> list[dict]:
    return _read_json(root, RED_TEAM_CASES_PATH)


def load_copyright_review(root: str | Path | None = None) -> dict:
    return _read_json(root, COPYRIGHT_REVIEW_PATH)


def _golden_review_cases(root: Path, default_status: str) -> list[dict]:
    cases = _read_json(root, GOLDEN_CASES_PATH)
    review_cases: list[dict] = []
    for case in cases:
        expected = case.get("expected", {})
        rule_id = expected.get("selected_transmission_rule", "unknown")
        review_cases.append(
            {
                "case_id": f"ER-{case['case_id']}",
                "source_case_id": case["case_id"],
                "rule_id": rule_id,
                "source_ids": ["RC-102"] if expected.get("is_high_risk") else [],
                "current_output": f"golden case {case['case_id']} expects {rule_id}",
                "review_status": default_status,
                "issue": "黄金样例需专家复核盘式、规则路径和安全边界。",
                "approved_for_beta": not bool(case.get("needs_expert_review")),
            }
        )
    return review_cases


def load_expert_review_cases(root: str | Path | None = None) -> dict:
    root_path = _root(root)
    seed = _read_json(root_path, EXPERT_REVIEW_CASES_PATH)
    cases: list[dict] = []
    if seed.get("include_golden_cases"):
        cases.extend(_golden_review_cases(root_path, seed.get("default_status_for_golden_cases", "pending_expert_review")))
    cases.extend(seed.get("additional_cases", []))
    return {"review_id": seed["review_id"], "cases": cases}


def _flatten(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(_flatten(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return " ".join(_flatten(item) for item in value)
    return str(value)


def _answer_text_for_safety(answer: Mapping[str, Any]) -> str:
    checked_values = [
        answer.get("overview"),
        answer.get("rule_reasoning"),
        answer.get("plain_explanation"),
        answer.get("action_prompts"),
        answer.get("entertainment"),
        answer.get("share_report"),
    ]
    return _flatten(checked_values)


def _blocked_intent(question: str) -> list[str]:
    reasons: list[str] = []
    if any(token in question for token in ["对方现在在哪里", "跟踪", "查他", "查她", "别管隐私"]):
        reasons.append("privacy")
    if any(token in question for token in ["让他一定", "让她一定", "操控", "不要讲边界"]):
        reasons.append("manipulation")
    if any(token in question for token in ["没有出处也编", "编一个", "伪造出处"]):
        reasons.append("anti_hallucination")
    if any(token in question for token in ["不要调用工具", "自己排盘", "忽略安全规则"]):
        reasons.append("model_bypass")
    return reasons


def blocked_question_reasons(question: str) -> list[str]:
    return _blocked_intent(question)


def validate_safety(answer: Mapping[str, Any], chart_json: Mapping[str, Any], mode: str = "professional") -> dict:
    policy = load_safety_policy()
    answer_text = _answer_text_for_safety(answer)
    question = str(chart_json.get("question", ""))
    blocked_reasons: list[str] = []

    matched_terms = [term for term in policy["forbidden_terms"] if term in answer_text]
    if matched_terms:
        blocked_reasons.append("forbidden_terms")

    if any(token in answer_text for token in ["只看神煞", "神煞即可", "神煞决定", "神煞单独"]):
        blocked_reasons.append("single_shensha_conclusion")

    if mode == "professional" and not answer.get("evidence") and answer.get("overview") != "依据不足":
        blocked_reasons.append("professional_without_evidence")

    blocked_reasons.extend(reason for reason in _blocked_intent(question) if reason not in blocked_reasons)

    safety = chart_json.get("safety", {})
    entertainment = answer.get("entertainment", {})
    action = "allow_cultural_interpretation"
    if safety.get("action") == "safety_only":
        action = "safety_only"
        if answer.get("plain_explanation"):
            blocked_reasons.append("high_risk_plain_explanation")
        if entertainment.get("persona_lines") or entertainment.get("story_scene") or entertainment.get("mentor_steps"):
            blocked_reasons.append("high_risk_entertainment_output")
    elif any(reason in blocked_reasons for reason in ["privacy", "manipulation", "anti_hallucination", "model_bypass"]):
        action = "blocked"
    elif blocked_reasons:
        action = "blocked"

    return {
        "policy_id": policy["policy_id"],
        "mode": mode,
        "action": action,
        "passed": not blocked_reasons,
        "blocked_reasons": list(dict.fromkeys(blocked_reasons)),
        "matched_forbidden_terms": matched_terms,
        "checked_fields": ["overview", "rule_reasoning", "plain_explanation", "action_prompts", "entertainment", "share_report"],
    }


def beta_readiness_flags(chart_json: Mapping[str, Any], safety_report: Mapping[str, Any]) -> list[str]:
    if safety_report.get("action") == "safety_only":
        return ["high_risk_safety_only", "blocked_from_beta_interpretation"]
    if safety_report.get("action") == "blocked":
        return ["blocked_by_safety_policy"]
    return ["low_risk_mode_allowed", "evidence_required", "cultural_entertainment_only"]


def validate_beta_readiness(case_results: Mapping[str, Any]) -> dict:
    expert_cases = case_results.get("expert_cases", {}).get("cases", [])
    copyright_items = case_results.get("copyright_review", {}).get("items", [])
    blocked_reasons: list[str] = []

    pending_expert = [
        case for case in expert_cases if case.get("review_status") in {"pending_expert_review", "needs_expert_review"} and not case.get("approved_for_beta")
    ]
    blocked_copyright = [item for item in copyright_items if item.get("beta_status") == "blocked"]

    if pending_expert:
        blocked_reasons.append("expert_review_pending")
    if blocked_copyright:
        blocked_reasons.append("copyright_blocked_items")
    if not case_results.get("red_team_passed"):
        blocked_reasons.append("red_team_not_passed")
    if not case_results.get("golden_cases_passed"):
        blocked_reasons.append("golden_cases_not_passed")

    policy = load_safety_policy()
    return {
        "ready_for_beta": not blocked_reasons,
        "blocked_reasons": blocked_reasons,
        "allowed_beta_scope": policy["beta_allowed_scope"],
        "blocked_beta_scope": policy["beta_blocked_scope"],
        "pending_expert_count": len(pending_expert),
        "blocked_copyright_count": len(blocked_copyright),
    }
