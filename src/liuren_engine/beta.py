from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


BETA_CONFIG_PATH = Path("data") / "beta_config.v0.1.json"
DEFAULT_FEEDBACK_PATH = Path("data") / "beta_feedback.v0.1.jsonl"
BETA_REPORT_PATH = Path("data") / "beta_test_report.v0.1.json"

SENSITIVE_KEYS = {
    "audio",
    "audio_blob",
    "audio_data",
    "recording",
    "openai_api_key",
    "api_key",
    "authorization",
    "secret",
}
HIGH_RISK_BETA_CATEGORIES = {"Q-009", "Q-010", "Q-011", "Q-012"}
REVIEW_FEEDBACK_TYPES = {"source_insufficient", "safety_issue", "chart_question"}
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.IGNORECASE),
]


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _feedback_path(root: str | Path | None = None, feedback_path: str | Path | None = None) -> Path:
    if feedback_path is not None:
        return Path(feedback_path)
    env_path = os.getenv("LIUREN_BETA_FEEDBACK_PATH")
    if env_path:
        return Path(env_path)
    return _root(root) / DEFAULT_FEEDBACK_PATH


def load_beta_config(root: str | Path | None = None) -> dict:
    return json.loads((_root(root) / BETA_CONFIG_PATH).read_text(encoding="utf-8"))


def tester_notice(root: str | Path | None = None) -> str:
    return str(load_beta_config(root).get("tester_notice", "受限 Beta：传统文化学习与娱乐体验。"))


def make_feedback_token(chart_id: str | None, mode: str, category: str | None = None) -> str:
    source = f"{chart_id or 'chart'}|{mode}|{category or 'unknown'}"
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    return f"fb_{digest}"


def beta_scope_for(chart_json: Mapping[str, Any], safety_report: Mapping[str, Any], mode: str, root: str | Path | None = None) -> dict:
    config = load_beta_config(root)
    category = str(chart_json.get("category") or chart_json.get("safety", {}).get("category") or "")
    blocked_reasons = list(safety_report.get("blocked_reasons") or [])
    allowed_modes = list(config.get("allowed_modes", []))
    allowed_categories = list(config.get("allowed_categories", []))
    blocked_categories = list(config.get("blocked_categories", []))

    if mode not in allowed_modes:
        return {
            "beta_id": config["beta_id"],
            "status": "blocked",
            "reason": "mode_not_allowed",
            "allowed_modes": allowed_modes,
            "allowed_categories": allowed_categories,
            "blocked_categories": blocked_categories,
        }
    if safety_report.get("action") == "safety_only" or category in blocked_categories:
        return {
            "beta_id": config["beta_id"],
            "status": "safety_only",
            "reason": "high_risk_category",
            "allowed_modes": allowed_modes,
            "allowed_categories": allowed_categories,
            "blocked_categories": blocked_categories,
        }
    if safety_report.get("action") == "blocked" or blocked_reasons:
        return {
            "beta_id": config["beta_id"],
            "status": "blocked",
            "reason": "safety_policy_blocked",
            "allowed_modes": allowed_modes,
            "allowed_categories": allowed_categories,
            "blocked_categories": blocked_categories,
        }
    if category and category not in allowed_categories:
        return {
            "beta_id": config["beta_id"],
            "status": "blocked",
            "reason": "category_not_in_limited_beta",
            "allowed_modes": allowed_modes,
            "allowed_categories": allowed_categories,
            "blocked_categories": blocked_categories,
        }
    return {
        "beta_id": config["beta_id"],
        "status": "allowed",
        "reason": "low_risk_limited_beta_scope",
        "allowed_modes": allowed_modes,
        "allowed_categories": allowed_categories,
        "blocked_categories": blocked_categories,
        "notice": config.get("tester_notice", ""),
    }


def beta_block_flags(beta_scope: Mapping[str, Any]) -> list[str]:
    status = beta_scope.get("status")
    reason = beta_scope.get("reason")
    if status == "allowed":
        return []
    if status == "safety_only":
        return ["blocked_from_beta_interpretation"]
    if reason == "mode_not_allowed":
        return ["beta_mode_not_allowed"]
    if reason == "category_not_in_limited_beta":
        return ["category_not_in_limited_beta"]
    return ["blocked_by_safety_policy"]


def _safe_scalar(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str):
            for pattern in SECRET_PATTERNS:
                value = pattern.sub("[redacted]", value)
        return value
    if isinstance(value, list):
        return [str(item) for item in value[:20]]
    return str(value)


def _sanitized_feedback(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "tester_id",
        "chart_id",
        "mode",
        "category",
        "safety_action",
        "blocked_reasons",
        "feedback_type",
        "note",
        "feedback_token",
        "beta_scope_status",
    }
    record = {key: _safe_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    lower_payload_keys = {str(key).lower() for key in payload.keys()}
    if lower_payload_keys & SENSITIVE_KEYS:
        record["dropped_sensitive_fields"] = sorted(lower_payload_keys & SENSITIVE_KEYS)
    record.setdefault("tester_id", "anonymous")
    record.setdefault("feedback_type", "helpful")
    record.setdefault("mode", "plain")
    record.setdefault("category", "")
    record.setdefault("blocked_reasons", [])
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    return record


def record_beta_feedback(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    feedback_path: str | Path | None = None,
) -> dict:
    path = _feedback_path(root, feedback_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = _sanitized_feedback(payload)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def load_beta_feedback(root: str | Path | None = None, feedback_path: str | Path | None = None) -> list[dict]:
    path = _feedback_path(root, feedback_path)
    if not path.exists():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("record_type") == "seed":
            continue
        records.append(record)
    return records


def _is_high_risk_record(record: Mapping[str, Any]) -> bool:
    return record.get("safety_action") == "safety_only" or record.get("category") in HIGH_RISK_BETA_CATEGORIES


def _is_blocked_record(record: Mapping[str, Any]) -> bool:
    return bool(record.get("blocked_reasons")) or record.get("safety_action") in {"safety_only", "blocked"}


def _manual_review_item(record: Mapping[str, Any]) -> dict | None:
    if not _is_blocked_record(record) and record.get("feedback_type") not in REVIEW_FEEDBACK_TYPES:
        return None
    return {
        "chart_id": record.get("chart_id"),
        "tester_id": record.get("tester_id"),
        "mode": record.get("mode"),
        "category": record.get("category"),
        "feedback_type": record.get("feedback_type"),
        "blocked_reasons": record.get("blocked_reasons", []),
        "note": record.get("note", ""),
        "timestamp": record.get("timestamp"),
    }


def build_beta_report(
    root: str | Path | None = None,
    feedback_path: str | Path | None = None,
) -> dict:
    config = load_beta_config(root)
    feedback = load_beta_feedback(root, feedback_path)
    chart_ids = {record.get("chart_id") for record in feedback if record.get("chart_id")}
    mode_distribution = Counter(str(record.get("mode", "unknown")) for record in feedback)
    feedback_distribution = Counter(str(record.get("feedback_type", "unknown")) for record in feedback)
    blocked_records = [record for record in feedback if _is_blocked_record(record)]
    manual_review_items = [item for record in feedback if (item := _manual_review_item(record))]
    return {
        "report_id": "beta_test_report.v0.1",
        "beta_id": config["beta_id"],
        "generated_at": _utc_now(),
        "session_count": len(chart_ids),
        "feedback_count": len(feedback),
        "completion_count": sum(1 for record in feedback if record.get("feedback_type") == "helpful"),
        "mode_distribution": dict(mode_distribution),
        "feedback_distribution": dict(feedback_distribution),
        "high_risk_trigger_count": sum(1 for record in feedback if _is_high_risk_record(record)),
        "safety_block_count": len(blocked_records),
        "failed_interface_count": sum(1 for record in feedback if record.get("feedback_type") == "voice_issue"),
        "manual_review_items": manual_review_items,
        "allowed_scope": {
            "modes": config.get("allowed_modes", []),
            "categories": config.get("allowed_categories", []),
        },
        "blocked_scope": {
            "categories": config.get("blocked_categories", []),
            "rules": config.get("blocked_scope_notes", []),
        },
    }
