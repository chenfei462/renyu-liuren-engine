from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .growth import build_growth_metrics, build_share_report_metrics, load_growth_events, validate_canary_access


CANARY_RUN_CONFIG_PATH = Path("data") / "canary_run_config.v0.1.json"
DEFAULT_SESSION_LOG_PATH = Path("data") / "canary_session_log.v0.1.jsonl"
CANARY_METRICS_PATH = Path("data") / "canary_metrics.v0.1.json"
PUBLIC_RELEASE_GATE_PATH = Path("data") / "public_release_gate.v0.1.json"
PHASE11_REPORT_PATH = Path("data") / "phase11_canary_report.v0.1.json"
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


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(root: str | Path | None, path: Path) -> Any:
    return json.loads((_root(root) / path).read_text(encoding="utf-8"))


def _session_log_path(root: str | Path | None = None, session_log_path: str | Path | None = None) -> Path:
    if session_log_path is not None:
        return Path(session_log_path)
    env_path = os.getenv("LIUREN_CANARY_SESSION_LOG_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_SESSION_LOG_PATH


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


def load_canary_run_config(root: str | Path | None = None) -> dict:
    return _read_json(root, CANARY_RUN_CONFIG_PATH)


def _sanitize_session(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "session_id",
        "tester_id",
        "invite_code",
        "chart_id",
        "mode",
        "category",
        "session_status",
        "feedback_type",
        "safety_action",
        "blocked_reasons",
        "latency_ms",
        "channel",
        "event_type",
        "incident_type",
        "source",
        "note",
    }
    lower_keys = {str(key).lower() for key in payload.keys()}
    record = {key: _clean_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    dropped = sorted(lower_keys & SENSITIVE_KEYS)
    if dropped:
        record["dropped_sensitive_field_count"] = len(dropped)
    record.setdefault("tester_id", "anonymous")
    record.setdefault("mode", "plain")
    record.setdefault("session_status", "started")
    record.setdefault("source", "local_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["session_id"] = str(
        payload.get("session_id")
        or f"canary_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}"
    )
    return record


def record_canary_session(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    session_log_path: str | Path | None = None,
) -> dict:
    record = _sanitize_session(payload)
    path = _session_log_path(root, session_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def load_canary_sessions(root: str | Path | None = None, session_log_path: str | Path | None = None) -> list[dict]:
    path = _session_log_path(root, session_log_path)
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


def _is_blocked_session(record: Mapping[str, Any]) -> bool:
    return bool(record.get("blocked_reasons")) or record.get("safety_action") in {"safety_only", "blocked"}


def _is_high_risk_trigger(record: Mapping[str, Any]) -> bool:
    return record.get("category") in HIGH_RISK_CATEGORIES or record.get("safety_action") == "safety_only"


def _count_incidents(records: list[Mapping[str, Any]], incident_type: str) -> int:
    return sum(1 for record in records if record.get("incident_type") == incident_type or record.get("event_type") == incident_type)


def build_canary_metrics(
    root: str | Path | None = None,
    session_log_path: str | Path | None = None,
    growth_events_path: str | Path | None = None,
) -> dict:
    sessions = load_canary_sessions(root, session_log_path)
    growth = build_growth_metrics(root, growth_events_path)
    mode_counts = Counter(str(session.get("mode", "unknown")) for session in sessions)
    feedback_counts = Counter(str(session.get("feedback_type", "none")) for session in sessions if session.get("feedback_type"))
    tester_counts: defaultdict[str, int] = defaultdict(int)
    for session in sessions:
        tester_id = str(session.get("tester_id") or "")
        if tester_id and tester_id != "anonymous":
            tester_counts[tester_id] += 1
    metrics = {
        "metrics_id": "canary_metrics.v0.1",
        "generated_at": _utc_now(),
        "session_count": len(sessions),
        "unique_tester_count": len(tester_counts),
        "returning_tester_count": sum(1 for count in tester_counts.values() if count >= 2),
        "completion_count": sum(1 for session in sessions if session.get("session_status") == "completed"),
        "story_mode_count": int(mode_counts.get("story", 0)),
        "mentor_mode_count": int(mode_counts.get("mentor", 0)),
        "professional_mode_count": int(mode_counts.get("professional", 0)),
        "plain_mode_count": int(mode_counts.get("plain", 0)),
        "feedback_submit_count": sum(1 for session in sessions if session.get("feedback_type")) + int(growth.get("feedback_submit_count", 0)),
        "learning_card_click_count": int(growth.get("learning_card_click_count", 0)),
        "member_interest_count": int(growth.get("member_interest_count", 0)),
        "course_interest_count": int(growth.get("course_interest_count", 0)),
        "business_interest_count": int(growth.get("business_interest_count", 0)),
        "safety_block_count": sum(1 for session in sessions if _is_blocked_session(session)),
        "high_risk_trigger_count": sum(1 for session in sessions if _is_high_risk_trigger(session)),
        "high_risk_leak_count": _count_incidents(sessions, "high_risk_leak"),
        "hallucination_incident_count": _count_incidents(sessions, "hallucination_incident"),
        "copyright_blocked_visible_count": _count_incidents(sessions, "copyright_blocked_visible"),
        "realtime_tool_bypass_count": _count_incidents(sessions, "realtime_tool_bypass"),
        "deterministic_promise_count": _count_incidents(sessions, "deterministic_promise"),
        "professional_without_evidence_count": _count_incidents(sessions, "professional_without_evidence"),
        "realtime_failure_count": _count_incidents(sessions, "realtime_failure")
        + sum(1 for session in sessions if session.get("session_status") == "realtime_failed"),
        "mode_distribution": dict(mode_counts),
        "feedback_distribution": dict(feedback_counts),
        "growth_metrics": growth,
    }
    metrics.update(
        build_share_report_metrics(
            {
                "share_report_generated": int(growth.get("share_report_generated_count", growth.get("share_report_count", 0)) or 0),
                "share_report_user_reached": int(growth.get("share_report_user_reach_count", 0) or 0),
            }
        )
    )
    return metrics


def _append_unique(target: list[str], items: list[str]) -> None:
    for item in items:
        if item and item not in target:
            target.append(item)


def _matches_identity(record: Mapping[str, Any], tester_id: str, invite_code: str) -> bool:
    if not tester_id and not invite_code:
        return False
    record_tester = str(record.get("tester_id") or "").strip()
    record_invite = str(record.get("invite_code") or "").strip()
    return (bool(tester_id) and record_tester == tester_id) or (bool(invite_code) and record_invite == invite_code)


def _task_catalog(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [dict(task) for task in config.get("tester_tasks") or []],
        key=lambda task: int(task.get("sort_order") or 0),
    )


def _find_task_session(
    sessions: list[Mapping[str, Any]],
    completion_rule: str,
) -> Mapping[str, Any] | None:
    for session in sessions:
        if completion_rule == "completed_voice_session":
            if session.get("session_status") == "completed" and str(session.get("channel") or "realtime") == "realtime":
                return session
        elif completion_rule == "story_or_mentor_session":
            if session.get("session_status") == "completed" and session.get("mode") in {"story", "mentor"}:
                return session
        elif completion_rule == "feedback_submitted":
            if session.get("feedback_type"):
                return session
    return None


def _find_task_event(
    growth_events: list[Mapping[str, Any]],
    completion_rule: str,
) -> Mapping[str, Any] | None:
    event_type_map = {
        "share_report_generated": "share_report_generated",
        "feedback_submitted": "feedback_submitted",
    }
    event_type = event_type_map.get(completion_rule)
    if not event_type:
        return None
    for event in growth_events:
        if event.get("event_type") == event_type:
            return event
    return None


def build_canary_task_status(
    root: str | Path | None = None,
    tester_id: str | None = None,
    invite_code: str | None = None,
    session_log_path: str | Path | None = None,
    growth_events_path: str | Path | None = None,
) -> dict[str, Any]:
    from .ops import build_ops_status

    config = load_canary_run_config(root)
    ops_status = build_ops_status(root)
    cohort_metrics = build_canary_metrics(root, session_log_path, growth_events_path)
    tester_id = str(tester_id or "").strip()
    invite_code = str(invite_code or "").strip()
    sessions = [
        session
        for session in load_canary_sessions(root, session_log_path)
        if _matches_identity(session, tester_id, invite_code)
    ]
    growth_events = [
        event
        for event in load_growth_events(root, growth_events_path)
        if _matches_identity(event, tester_id, invite_code)
    ]

    validation = None
    identity_status = "missing"
    if tester_id or invite_code:
        validation = validate_canary_access({"tester_id": tester_id, "invite_code": invite_code}, root=root)
        identity_status = "matched" if validation.get("allowed") else "invalid"

    tasks: list[dict[str, Any]] = []
    completed_count = 0
    next_task_id = ""
    for task in _task_catalog(config):
        completion_rule = str(task.get("completion_rule") or "")
        matching_session = _find_task_session(sessions, completion_rule)
        matching_event = _find_task_event(growth_events, completion_rule)
        completed_record = matching_event or matching_session
        completed = completed_record is not None
        if completed:
            completed_count += 1
        elif not next_task_id:
            next_task_id = str(task.get("task_id") or "")
        task_status = "completed" if completed else "todo"
        if not completed and ops_status.get("status") != "canary":
            task_status = "blocked"
        tasks.append(
            {
                **task,
                "status": task_status,
                "completed": completed,
                "completed_at": str(completed_record.get("timestamp") or "") if completed_record else "",
                "evidence_count": 1 if completed_record else 0,
            }
        )

    total_tasks = len(tasks)
    tester_progress = {
        "completed_task_count": completed_count,
        "total_task_count": total_tasks,
        "completed_voice_session_count": sum(
            1
            for session in sessions
            if session.get("session_status") == "completed" and str(session.get("channel") or "realtime") == "realtime"
        ),
        "story_or_mentor_session_count": sum(1 for session in sessions if session.get("mode") in {"story", "mentor"}),
        "share_report_count": sum(1 for event in growth_events if event.get("event_type") == "share_report_generated"),
        "feedback_submit_count": sum(1 for event in growth_events if event.get("event_type") == "feedback_submitted"),
        "next_task_id": next_task_id,
    }

    overall_status = "completed" if total_tasks and completed_count == total_tasks else "todo"
    if completed_count and completed_count < total_tasks:
        overall_status = "in_progress"
    if ops_status.get("status") != "canary":
        overall_status = "blocked"

    return {
        "status_id": "canary_task_status.v0.1",
        "generated_at": _utc_now(),
        "tester_id": tester_id,
        "invite_code_present": bool(invite_code),
        "identity_status": identity_status,
        "validation": validation,
        "overall_status": overall_status,
        "ops_status": {
            "status": ops_status.get("status"),
            "blocked_reasons": list(ops_status.get("blocked_reasons") or []),
            "notice": ops_status.get("notice", ""),
        },
        "cohort_progress": {
            "session_count": int(cohort_metrics.get("session_count", 0)),
            "feedback_submit_count": int(cohort_metrics.get("feedback_submit_count", 0)),
            "share_report_count": int(cohort_metrics.get("share_report_count", 0)),
            "returning_tester_count": int(cohort_metrics.get("returning_tester_count", 0)),
            "thresholds": dict(config.get("public_release_thresholds", {})),
        },
        "tester_progress": tester_progress,
        "tasks": tasks,
    }


def build_public_release_gate(
    root: str | Path | None = None,
    ops_status: Mapping[str, Any] | None = None,
    canary_metrics: Mapping[str, Any] | None = None,
    release_readiness: Mapping[str, Any] | None = None,
) -> dict:
    from .ops import build_ops_status
    from .release import build_release_readiness

    config = load_canary_run_config(root)
    ops = dict(ops_status or build_ops_status(root))
    metrics = dict(canary_metrics or build_canary_metrics(root))
    readiness = dict(release_readiness or build_release_readiness(root))
    blocked_reasons: list[str] = []

    if ops.get("status") != "canary":
        blocked_reasons.append("canary_not_active")
    canary_gate = dict(ops.get("canary_gate") or {})
    if not canary_gate.get("canary_allowed"):
        blocked_reasons.append("expert_review_pending")
    _append_unique(blocked_reasons, list(ops.get("blocked_reasons") or []))
    _append_unique(blocked_reasons, list(readiness.get("blocked_reasons") or []))

    thresholds = dict(config.get("public_release_thresholds", {}))
    if int(metrics.get("session_count", 0)) < int(thresholds.get("min_sessions", 20)):
        blocked_reasons.append("insufficient_canary_sessions")
    if int(metrics.get("returning_tester_count", 0)) < int(thresholds.get("min_returning_testers", 5)):
        blocked_reasons.append("insufficient_returning_testers")
    if int(metrics.get("feedback_submit_count", 0)) < int(thresholds.get("min_feedback_submissions", 10)):
        blocked_reasons.append("insufficient_feedback")
    if int(metrics.get("share_report_count", 0)) < int(thresholds.get("min_share_reports", 3)):
        blocked_reasons.append("insufficient_share_reports")

    incident_map = {
        "high_risk_leak_count": "high_risk_leak_detected",
        "hallucination_incident_count": "hallucination_incident_detected",
        "copyright_blocked_visible_count": "copyright_blocked_visible",
        "realtime_tool_bypass_count": "realtime_tool_bypass_detected",
        "deterministic_promise_count": "deterministic_promise_detected",
        "professional_without_evidence_count": "professional_without_evidence_detected",
    }
    for metric_key, reason in incident_map.items():
        if int(metrics.get(metric_key, 0)) > 0:
            blocked_reasons.append(reason)

    blocked_reasons = list(dict.fromkeys(blocked_reasons))
    gate_status = "blocked" if blocked_reasons else "ready_for_phase12"
    return {
        "gate_id": "public_release_gate.v0.1",
        "generated_at": _utc_now(),
        "gate_status": gate_status,
        "blocked_reasons": blocked_reasons,
        "canary_metrics_id": metrics.get("metrics_id", "canary_metrics.v0.1"),
        "release_status": readiness.get("release_status"),
        "ops_status": ops.get("status"),
        "thresholds": thresholds,
        "next_step": "prepare_public_release" if gate_status == "ready_for_phase12" else "return_to_canary_or_review_fix",
    }


def build_phase11_report(
    root: str | Path | None = None,
    session_log_path: str | Path | None = None,
    growth_events_path: str | Path | None = None,
    ops_status: Mapping[str, Any] | None = None,
) -> dict:
    metrics = build_canary_metrics(root, session_log_path, growth_events_path)
    gate = build_public_release_gate(root, ops_status=ops_status, canary_metrics=metrics)
    recommendation = "advance_to_phase12" if gate.get("gate_status") == "ready_for_phase12" else "do_not_publicly_release"
    return {
        "report_id": "phase11_canary_report.v0.1",
        "generated_at": _utc_now(),
        "canary_metrics": metrics,
        "public_release_gate": gate,
        "recommendation": recommendation,
    }
