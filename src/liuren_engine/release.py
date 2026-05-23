from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .beta import build_beta_report
from .safety_review import load_copyright_review, load_expert_review_cases


RELEASE_CONFIG_PATH = Path("data") / "release_config.v0.1.json"
RELEASE_READINESS_PATH = Path("data") / "release_readiness.v0.1.json"
RELEASE_METRICS_PATH = Path("data") / "release_metrics.v0.1.json"
LAUNCH_CHECKLIST_PATH = Path("data") / "launch_checklist.v0.1.json"
LEGAL_DOCUMENTS = {
    "privacy": Path("docs") / "privacy_policy.v0.1.md",
    "safety": Path("docs") / "safety_boundaries.v0.1.md",
    "copyright": Path("docs") / "copyright_notice.v0.1.md",
}


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _read_json(root: str | Path | None, path: Path) -> Any:
    return json.loads((_root(root) / path).read_text(encoding="utf-8"))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_release_config(root: str | Path | None = None) -> dict:
    return _read_json(root, RELEASE_CONFIG_PATH)


def load_launch_checklist(root: str | Path | None = None) -> dict:
    return _read_json(root, LAUNCH_CHECKLIST_PATH)


def load_legal_document(kind: str, root: str | Path | None = None) -> dict:
    if kind not in LEGAL_DOCUMENTS:
        raise KeyError(f"unknown legal document: {kind}")
    path = _root(root) / LEGAL_DOCUMENTS[kind]
    content = path.read_text(encoding="utf-8")
    title = next((line.lstrip("# ").strip() for line in content.splitlines() if line.startswith("# ")), kind)
    return {
        "document_id": f"{kind}.v0.1",
        "kind": kind,
        "title": title,
        "content": content,
        "format": "markdown",
    }


def _pending_expert_rules(expert_review: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    rules: list[str] = []
    cases: list[str] = []
    for case in expert_review.get("cases", []):
        status = case.get("review_status")
        if case.get("approved_for_beta") is False or status in {"needs_expert_review", "pending_expert_review"}:
            rule_id = str(case.get("rule_id") or "")
            if not rule_id and str(case.get("case_id", "")).startswith("ER-"):
                rule_id = str(case["case_id"]).split("-")[1].lower()
            if rule_id and rule_id not in {"unknown", "safety_only"}:
                rules.append(rule_id)
            if case.get("case_id"):
                cases.append(str(case["case_id"]))
    return sorted(set(rules)), sorted(set(cases))


def _visible_blocked_copyright(copyright_review: Mapping[str, Any]) -> list[str]:
    return [
        str(item.get("item_id"))
        for item in copyright_review.get("items", [])
        if item.get("beta_status") == "blocked" and item.get("in_user_visible_product") is True
    ]


def build_release_readiness(
    root: str | Path | None = None,
    beta_report: Mapping[str, Any] | None = None,
    expert_review: Mapping[str, Any] | None = None,
    copyright_review: Mapping[str, Any] | None = None,
    red_team_passed: bool = True,
    golden_cases_passed: bool = True,
) -> dict:
    config = load_release_config(root)
    beta = dict(beta_report or build_beta_report(root))
    expert = dict(expert_review or load_expert_review_cases(root))
    copyright = dict(copyright_review or load_copyright_review(root))

    blocked_reasons: list[str] = []
    if int(beta.get("safety_leak_count", beta.get("high_risk_leak_count", 0)) or 0) > 0:
        blocked_reasons.append("high_risk_leak_detected")
    if int(beta.get("hallucination_incident_count", 0) or 0) > 0:
        blocked_reasons.append("hallucination_incident_detected")
    if int(beta.get("realtime_tool_bypass_count", 0) or 0) > 0:
        blocked_reasons.append("realtime_tool_bypass_detected")
    if int(beta.get("safety_block_count", 0) or 0) > 0:
        blocked_reasons.append("beta_safety_blocks_pending")
    if beta.get("manual_review_items"):
        blocked_reasons.append("beta_manual_review_pending")
    if not red_team_passed:
        blocked_reasons.append("red_team_not_passed")
    if not golden_cases_passed:
        blocked_reasons.append("golden_cases_not_passed")

    pending_rules, pending_cases = _pending_expert_rules(expert)
    if pending_rules:
        blocked_reasons.append("expert_review_pending")

    visible_blocked = _visible_blocked_copyright(copyright)
    if visible_blocked:
        blocked_reasons.append("copyright_blocked_visible")

    blocked_reasons = list(dict.fromkeys(blocked_reasons))
    return {
        "readiness_id": "release_readiness.v0.1",
        "release_id": config["release_id"],
        "generated_at": _utc_now(),
        "release_status": "blocked" if blocked_reasons else "ready",
        "blocked_reasons": blocked_reasons,
        "allowed_for_mvp": {
            "modes": config.get("allowed_modes", []),
            "categories": config.get("allowed_categories", []),
            "features": config.get("allowed_features", []),
        },
        "blocked_for_mvp": {
            "categories": config.get("blocked_categories", []),
            "features": config.get("blocked_features", []),
            "copyright_items": visible_blocked,
        },
        "needs_expert_review": {
            "rules": pending_rules,
            "cases": pending_cases[:50],
            "case_count": len(pending_cases),
        },
        "checked_inputs": {
            "beta_report_id": beta.get("report_id", "beta_test_report.v0.1"),
            "expert_review_id": expert.get("review_id", "expert_review_cases.v0.1"),
            "copyright_review_id": copyright.get("review_id", "copyright_review.v0.1"),
            "red_team_passed": red_team_passed,
            "golden_cases_passed": golden_cases_passed,
        },
    }


def build_release_metrics(root: str | Path | None = None, beta_report: Mapping[str, Any] | None = None) -> dict:
    config = load_release_config(root)
    beta = dict(beta_report or build_beta_report(root))
    sessions = int(beta.get("session_count", 0) or 0)
    completions = int(beta.get("completion_count", 0) or 0)
    mode_distribution = Counter(beta.get("mode_distribution", {}))
    feedback_distribution = Counter(beta.get("feedback_distribution", {}))
    return {
        "metrics_id": "release_metrics.v0.1",
        "release_id": config["release_id"],
        "generated_at": _utc_now(),
        "session_count": sessions,
        "completion_count": completions,
        "completion_rate": round(completions / sessions, 3) if sessions else 0,
        "feedback_count": int(beta.get("feedback_count", 0) or 0),
        "mode_distribution": dict(mode_distribution),
        "feedback_distribution": dict(feedback_distribution),
        "story_or_mentor_count": int(mode_distribution.get("story", 0)) + int(mode_distribution.get("mentor", 0)),
        "safety_block_count": int(beta.get("safety_block_count", 0) or 0),
        "high_risk_trigger_count": int(beta.get("high_risk_trigger_count", 0) or 0),
        "failed_interface_count": int(beta.get("failed_interface_count", 0) or 0),
        "realtime_failure_count": int(beta.get("realtime_failure_count", beta.get("failed_interface_count", 0)) or 0),
        "manual_review_count": len(beta.get("manual_review_items", []) or []),
    }
