from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .growth import build_growth_metrics, build_share_report_metrics


PUBLIC_CONFIG_PATH = Path("data") / "public_launch_config.v0.1.json"
DEFAULT_PUBLIC_SESSION_LOG_PATH = Path("data") / "public_session_log.v0.1.jsonl"
DEFAULT_PUBLIC_INCIDENTS_PATH = Path("data") / "public_incidents.v0.1.jsonl"
PUBLIC_METRICS_PATH = Path("data") / "public_metrics.v0.1.json"
PHASE12_REPORT_PATH = Path("data") / "phase12_public_launch_report.v0.1.json"

HIGH_RISK_CATEGORIES = {"Q-009", "Q-010", "Q-011", "Q-012"}
SENSITIVE_KEYS = {
    "audio",
    "audio_blob",
    "audio_data",
    "recording",
    "openai_api_key",
    "api_key",
    "authorization",
    "secret",
    "raw_input",
    "transcript",
}
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.IGNORECASE),
]
CRITICAL_EVENT_TYPES = {
    "high_risk_leak",
    "deterministic_promise",
    "professional_without_evidence",
    "copyright_complaint",
    "realtime_tool_bypass",
    "privacy_delete_request",
    "manual_public_pause",
}


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(root: str | Path | None, path: Path) -> Any:
    return json.loads((_root(root) / path).read_text(encoding="utf-8"))


def _public_session_log_path(root: str | Path | None = None, session_log_path: str | Path | None = None) -> Path:
    if session_log_path is not None:
        return Path(session_log_path)
    env_path = os.getenv("LIUREN_PUBLIC_SESSION_LOG_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_PUBLIC_SESSION_LOG_PATH


def _public_incidents_path(root: str | Path | None = None, incidents_path: str | Path | None = None) -> Path:
    if incidents_path is not None:
        return Path(incidents_path)
    env_path = os.getenv("LIUREN_PUBLIC_INCIDENTS_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_PUBLIC_INCIDENTS_PATH


def _clean_scalar(value: Any) -> Any:
    if isinstance(value, str):
        for pattern in SECRET_PATTERNS:
            value = pattern.sub("[redacted]", value)
        return value[:1000]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [str(item)[:200] for item in value[:20]]
    return str(value)[:1000]


def _append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _load_jsonl(path: Path) -> list[dict]:
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


def load_public_launch_config(root: str | Path | None = None) -> dict:
    return _read_json(root, PUBLIC_CONFIG_PATH)


def _sanitize_public_session(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "session_id",
        "visitor_id",
        "tester_id",
        "chart_id",
        "mode",
        "category",
        "session_status",
        "feedback_type",
        "safety_action",
        "blocked_reasons",
        "latency_ms",
        "event_type",
        "incident_type",
        "source",
        "note",
        "delete_request",
    }
    lower_keys = {str(key).lower() for key in payload.keys()}
    record = {key: _clean_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    dropped = lower_keys & SENSITIVE_KEYS
    if dropped:
        record["dropped_sensitive_field_count"] = len(dropped)
    record.setdefault("visitor_id", "anonymous")
    record.setdefault("mode", "plain")
    record.setdefault("session_status", "started")
    record.setdefault("source", "public_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["session_id"] = str(
        payload.get("session_id")
        or f"public_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}"
    )
    return record


def record_public_session(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    session_log_path: str | Path | None = None,
) -> dict:
    record = _sanitize_public_session(payload)
    _append_jsonl(_public_session_log_path(root, session_log_path), record)
    return record


def load_public_sessions(root: str | Path | None = None, session_log_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_public_session_log_path(root, session_log_path))


def _sanitize_public_incident(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "event_id",
        "event_type",
        "severity",
        "summary",
        "chart_id",
        "visitor_id",
        "source",
        "reason",
        "status",
    }
    lower_keys = {str(key).lower() for key in payload.keys()}
    record = {key: _clean_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    dropped = lower_keys & SENSITIVE_KEYS
    if dropped:
        record["dropped_sensitive_field_count"] = len(dropped)
    record.setdefault("event_type", "public_note")
    record.setdefault("severity", "P3")
    record.setdefault("summary", record.get("reason", "public event"))
    record.setdefault("source", "public_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["event_id"] = str(
        record.get("event_id")
        or f"public_incident_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}"
    )
    return record


def record_public_incident(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    incidents_path: str | Path | None = None,
) -> dict:
    record = _sanitize_public_incident(payload)
    _append_jsonl(_public_incidents_path(root, incidents_path), record)
    return record


def load_public_incidents(root: str | Path | None = None, incidents_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_public_incidents_path(root, incidents_path))


def _active_critical_incidents(incidents: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    active: list[Mapping[str, Any]] = []
    for incident in incidents:
        if incident.get("event_type") == "manual_public_resume":
            active.clear()
            continue
        if incident.get("event_type") in CRITICAL_EVENT_TYPES or incident.get("severity") in {"P0", "P1"}:
            active.append(incident)
    return active


def _is_blocked_session(record: Mapping[str, Any]) -> bool:
    return bool(record.get("blocked_reasons")) or record.get("safety_action") in {"safety_only", "blocked"}


def _is_high_risk_trigger(record: Mapping[str, Any]) -> bool:
    return record.get("category") in HIGH_RISK_CATEGORIES or record.get("safety_action") == "safety_only"


def build_public_metrics(
    root: str | Path | None = None,
    session_log_path: str | Path | None = None,
    growth_events_path: str | Path | None = None,
    incidents_path: str | Path | None = None,
) -> dict:
    sessions = load_public_sessions(root, session_log_path)
    incidents = load_public_incidents(root, incidents_path)
    growth = build_growth_metrics(root, growth_events_path)
    mode_counts = Counter(str(session.get("mode", "unknown")) for session in sessions)
    feedback_counts = Counter(str(session.get("feedback_type", "none")) for session in sessions if session.get("feedback_type"))
    event_counts = Counter(str(session.get("event_type", "unknown")) for session in sessions if session.get("event_type"))
    incident_counts = Counter(str(incident.get("event_type", "unknown")) for incident in incidents if incident.get("event_type"))
    completion_count = sum(1 for session in sessions if session.get("session_status") == "completed")
    share_report_generated_count = int(growth.get("share_report_generated_count", growth.get("share_report_count", 0)) or 0) + int(
        event_counts.get("share_report_generated", 0)
    )
    share_report_user_reach_count = int(growth.get("share_report_user_reach_count", 0) or 0) + int(
        event_counts.get("share_report_user_reached", 0)
    )
    feedback_submit_count = sum(1 for session in sessions if session.get("feedback_type")) + int(growth.get("feedback_submit_count", 0))
    realtime_failure_count = (
        int(event_counts.get("realtime_failure", 0))
        + int(incident_counts.get("realtime_failure", 0))
        + sum(1 for session in sessions if session.get("session_status") == "realtime_failed")
    )
    api_failure_count = int(event_counts.get("api_failure", 0)) + int(incident_counts.get("api_failure", 0))
    metrics = {
        "metrics_id": "public_metrics.v0.1",
        "generated_at": _utc_now(),
        "session_count": len(sessions),
        "completion_count": completion_count,
        "completion_rate": round(completion_count / len(sessions), 3) if sessions else 0,
        "feedback_submit_count": feedback_submit_count,
        "feedback_distribution": dict(feedback_counts),
        "mode_distribution": dict(mode_counts),
        "professional_mode_count": int(mode_counts.get("professional", 0)),
        "plain_mode_count": int(mode_counts.get("plain", 0)),
        "story_mode_count": int(mode_counts.get("story", 0)),
        "mentor_mode_count": int(mode_counts.get("mentor", 0)),
        "safety_block_count": sum(1 for session in sessions if _is_blocked_session(session)),
        "high_risk_trigger_count": sum(1 for session in sessions if _is_high_risk_trigger(session)),
        "api_failure_count": api_failure_count,
        "realtime_failure_count": realtime_failure_count,
        "learning_card_click_count": int(growth.get("learning_card_click_count", 0)),
        "member_interest_count": int(growth.get("member_interest_count", 0)),
        "course_interest_count": int(growth.get("course_interest_count", 0)),
        "business_interest_count": int(growth.get("business_interest_count", 0)),
        "critical_incident_count": len(_active_critical_incidents(incidents)),
        "incident_distribution": dict(incident_counts),
        "growth_metrics": growth,
    }
    metrics.update(
        build_share_report_metrics(
            {
                "share_report_generated": share_report_generated_count,
                "share_report_user_reached": share_report_user_reach_count,
            }
        )
    )
    return metrics


def _append_unique(target: list[str], items: Sequence[str]) -> None:
    for item in items:
        if item and item not in target:
            target.append(item)


def build_public_status(
    root: str | Path | None = None,
    public_release_gate: Mapping[str, Any] | None = None,
    incidents: Sequence[Mapping[str, Any]] | None = None,
    desired_status: str | None = None,
) -> dict:
    from .canary_run import build_public_release_gate

    config = load_public_launch_config(root)
    gate = dict(public_release_gate or build_public_release_gate(root))
    incident_records = list(incidents if incidents is not None else load_public_incidents(root))
    critical = _active_critical_incidents(incident_records)
    blocked_reasons: list[str] = []
    launch_status = str(desired_status or config.get("desired_status", "preview"))
    pause_reason = ""

    if critical:
        launch_status = "paused"
        pause_reason = "critical_public_incident"
        blocked_reasons.append("critical_public_incident")
    elif gate.get("gate_status") != "ready_for_phase12":
        launch_status = "blocked"
        blocked_reasons.append("public_release_gate_blocked")
        _append_unique(blocked_reasons, list(gate.get("blocked_reasons") or []))
    elif launch_status not in {"preview", "live"}:
        launch_status = "blocked"
        blocked_reasons.append("public_launch_not_enabled")

    return {
        "status_id": "public_status.v0.1",
        "generated_at": _utc_now(),
        "launch_status": launch_status,
        "public_launch_status": launch_status,
        "pause_reason": pause_reason,
        "blocked_reasons": blocked_reasons,
        "gate_status": gate.get("gate_status"),
        "public_release_gate": gate,
        "allowed_scope": ["low_risk_public_mvp"] if not blocked_reasons else [],
        "allowed_categories": config.get("allowed_categories", []),
        "blocked_categories": config.get("blocked_categories", []),
        "notice": config.get("public_notice", ""),
        "critical_incident_count": len(critical),
    }


def build_phase12_report(
    root: str | Path | None = None,
    session_log_path: str | Path | None = None,
    growth_events_path: str | Path | None = None,
    incidents_path: str | Path | None = None,
    public_release_gate: Mapping[str, Any] | None = None,
) -> dict:
    incidents = load_public_incidents(root, incidents_path)
    status = build_public_status(root=root, public_release_gate=public_release_gate, incidents=incidents)
    metrics = build_public_metrics(root, session_log_path, growth_events_path, incidents_path)
    if status.get("launch_status") == "paused":
        decision = "pause_and_fix"
    elif status.get("launch_status") in {"preview", "live"}:
        decision = "continue_public_mvp_observation"
    else:
        decision = "do_not_open_public_mvp"
    return {
        "report_id": "phase12_public_launch_report.v0.1",
        "generated_at": _utc_now(),
        "public_status": status,
        "public_metrics": metrics,
        "decision": decision,
        "next_step": "phase13_productization" if decision == "continue_public_mvp_observation" else "return_to_phase10_or_phase11_fix",
        "blocked_review_list": status.get("blocked_reasons", []),
    }
