from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .beta import build_beta_report, load_beta_feedback
from .growth import build_review_gate, build_share_report_metrics
from .release import build_release_readiness


OPS_CONFIG_PATH = Path("data") / "ops_config.v0.1.json"
OPS_METRICS_PATH = Path("data") / "ops_metrics.v0.1.json"
DEFAULT_EVENTS_PATH = Path("data") / "ops_events.v0.1.jsonl"
FEEDBACK_TRIAGE_PATH = Path("data") / "feedback_triage.v0.1.json"
OPS_REPORT_PATH = Path("data") / "phase9_ops_report.v0.1.json"
HIGH_RISK_CATEGORIES = {"Q-009", "Q-010", "Q-011", "Q-012"}
REVIEW_FEEDBACK_TYPES = {"safety_issue", "source_insufficient", "chart_question"}
CRITICAL_EVENT_TYPES = {
    "high_risk_leak",
    "deterministic_promise",
    "professional_without_evidence",
    "privacy_delete_request",
    "copyright_complaint",
    "realtime_tool_bypass",
    "manual_pause",
}
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.IGNORECASE),
]


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(root: str | Path | None, path: Path) -> Any:
    return json.loads((_root(root) / path).read_text(encoding="utf-8"))


def _events_path(root: str | Path | None = None, events_path: str | Path | None = None) -> Path:
    if events_path is not None:
        return Path(events_path)
    env_path = os.getenv("LIUREN_OPS_EVENTS_PATH")
    if env_path:
        return Path(env_path)
    return _root(root) / DEFAULT_EVENTS_PATH


def _clean_text(value: Any) -> Any:
    if isinstance(value, str):
        for pattern in SECRET_PATTERNS:
            value = pattern.sub("[redacted]", value)
        return value[:1000]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [str(item)[:200] for item in value[:20]]
    return str(value)[:1000]


def load_ops_config(root: str | Path | None = None) -> dict:
    return _read_json(root, OPS_CONFIG_PATH)


def record_ops_event(payload: Mapping[str, Any], root: str | Path | None = None, events_path: str | Path | None = None) -> dict:
    allowed = {"event_id", "event_type", "severity", "summary", "chart_id", "tester_id", "source", "reason"}
    record = {key: _clean_text(payload.get(key)) for key in allowed if key in payload}
    record.setdefault("event_type", "ops_note")
    record.setdefault("severity", "P3")
    record.setdefault("summary", record.get("reason", "ops event"))
    record.setdefault("source", "local_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["event_id"] = str(record.get("event_id") or f"ops_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}")
    path = _events_path(root, events_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def load_ops_events(root: str | Path | None = None, events_path: str | Path | None = None) -> list[dict]:
    path = _events_path(root, events_path)
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


def _manual_pause_active(events: Sequence[Mapping[str, Any]]) -> bool:
    state = False
    for event in events:
        if event.get("event_type") == "manual_pause":
            state = True
        elif event.get("event_type") == "manual_resume":
            state = False
    return state


def _critical_events(events: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    critical: list[Mapping[str, Any]] = []
    for event in events:
        if event.get("event_type") == "manual_resume":
            critical.clear()
            continue
        if event.get("event_type") in CRITICAL_EVENT_TYPES or event.get("severity") in {"P0", "P1"}:
            critical.append(event)
    return critical


def build_ops_status(
    root: str | Path | None = None,
    release_readiness: Mapping[str, Any] | None = None,
    events: Sequence[Mapping[str, Any]] | None = None,
) -> dict:
    config = load_ops_config(root)
    readiness = dict(release_readiness or build_release_readiness(root))
    review_gate = build_review_gate(root)
    blocked_reasons = list(readiness.get("blocked_reasons", []))
    if review_gate.get("canary_allowed"):
        blocked_reasons = [reason for reason in blocked_reasons if reason != "expert_review_pending"]
    elif "expert_review_pending" not in blocked_reasons:
        blocked_reasons.append("expert_review_pending")
    event_records = list(events if events is not None else load_ops_events(root))
    critical = _critical_events(event_records)
    status = "canary"
    pause_reason = ""
    if _manual_pause_active(event_records):
        status = "paused"
        pause_reason = "manual_pause"
    elif critical:
        status = "paused"
        pause_reason = "critical_ops_event"
    elif blocked_reasons or (readiness.get("release_status") == "blocked" and not review_gate.get("canary_allowed")):
        status = "blocked"
        pause_reason = "release_readiness_blocked"
    review_rules = sorted(
        set(readiness.get("needs_expert_review", {}).get("rules", []) or [])
        | set(review_gate.get("blocked_rules", []) or [])
    )
    return {
        "ops_id": config["ops_id"],
        "status": status,
        "release_status": readiness.get("release_status"),
        "pause_reason": pause_reason,
        "blocked_reasons": blocked_reasons,
        "critical_event_count": len(critical),
        "manual_pause_active": _manual_pause_active(event_records),
        "allowed_tester_count": config.get("canary_user_limit", 50),
        "review_queue": {
            **readiness.get("needs_expert_review", {"rules": [], "cases": [], "case_count": 0}),
            "rules": review_rules,
        },
        "canary_gate": review_gate,
        "notice": config.get("status_notices", {}).get(status, ""),
    }


def build_ops_metrics(
    root: str | Path | None = None,
    beta_report: Mapping[str, Any] | None = None,
    events: Sequence[Mapping[str, Any]] | None = None,
) -> dict:
    beta = dict(beta_report or build_beta_report(root))
    event_records = list(events if events is not None else load_ops_events(root))
    event_counts = Counter(str(event.get("event_type", "unknown")) for event in event_records)
    sessions = int(beta.get("session_count", 0) or 0)
    completions = int(beta.get("completion_count", 0) or 0)
    metrics = {
        "metrics_id": "ops_metrics.v0.1",
        "ops_id": load_ops_config(root)["ops_id"],
        "generated_at": _utc_now(),
        "session_count": sessions,
        "completion_count": completions,
        "completion_rate": round(completions / sessions, 3) if sessions else 0,
        "feedback_count": int(beta.get("feedback_count", 0) or 0),
        "mode_distribution": dict(beta.get("mode_distribution", {})),
        "feedback_distribution": dict(beta.get("feedback_distribution", {})),
        "safety_block_count": int(beta.get("safety_block_count", 0) or 0),
        "high_risk_trigger_count": int(beta.get("high_risk_trigger_count", 0) or 0),
        "api_failure_count": int(event_counts.get("api_failure", 0)),
        "realtime_failure_count": int(event_counts.get("realtime_failure", 0)) + int(beta.get("realtime_failure_count", 0) or 0),
        "failed_interface_count": int(beta.get("failed_interface_count", 0) or 0),
        "critical_event_count": len(_critical_events(event_records)),
        "manual_pause_count": int(event_counts.get("manual_pause", 0)),
        "business_interest_count": int(event_counts.get("business_interest", 0)),
    }
    metrics.update(build_share_report_metrics(event_counts))
    return metrics


def _review_reasons(record: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if record.get("blocked_reasons"):
        reasons.append("blocked_reasons")
    if record.get("category") in HIGH_RISK_CATEGORIES or record.get("safety_action") == "safety_only":
        reasons.append("high_risk_category")
    if record.get("feedback_type") in REVIEW_FEEDBACK_TYPES:
        reasons.append(str(record["feedback_type"]))
    return reasons


def build_feedback_triage(
    root: str | Path | None = None,
    feedback_path: str | Path | None = None,
) -> dict:
    feedback = load_beta_feedback(root, feedback_path)
    items: list[dict] = []
    status_counts: Counter[str] = Counter()
    for record in feedback:
        reasons = _review_reasons(record)
        triage_status = "needs_expert_review" if reasons else "new"
        status_counts[triage_status] += 1
        items.append(
            {
                "chart_id": record.get("chart_id"),
                "tester_id": record.get("tester_id"),
                "mode": record.get("mode"),
                "category": record.get("category"),
                "feedback_type": record.get("feedback_type"),
                "triage_status": triage_status,
                "review_reasons": reasons,
                "note": record.get("note", ""),
                "timestamp": record.get("timestamp"),
            }
        )
    return {
        "triage_id": "feedback_triage.v0.1",
        "generated_at": _utc_now(),
        "summary": {
            "total_feedback": len(feedback),
            "new": status_counts.get("new", 0),
            "needs_expert_review": status_counts.get("needs_expert_review", 0),
        },
        "items": items,
    }


def build_ops_report(
    root: str | Path | None = None,
    status: Mapping[str, Any] | None = None,
    metrics: Mapping[str, Any] | None = None,
    triage: Mapping[str, Any] | None = None,
) -> dict:
    ops_status = dict(status or build_ops_status(root))
    ops_metrics = dict(metrics or build_ops_metrics(root))
    feedback_triage = dict(triage or build_feedback_triage(root))
    decision = "do_not_open" if ops_status.get("status") == "blocked" else ("pause_and_fix" if ops_status.get("status") == "paused" else "canary_continue")
    return {
        "report_id": "phase9_ops_report.v0.1",
        "ops_id": load_ops_config(root)["ops_id"],
        "generated_at": _utc_now(),
        "status": ops_status,
        "metrics": ops_metrics,
        "feedback_triage": feedback_triage,
        "decision": decision,
    }
