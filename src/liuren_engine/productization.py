from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PRODUCTIZATION_CONFIG_PATH = Path("data") / "productization_config.v0.1.json"
PRODUCTIZATION_GATE_PATH = Path("data") / "productization_gate.v0.1.json"
DEFAULT_VISITOR_PROFILE_PATH = Path("data") / "visitor_profile.v0.1.jsonl"
DEFAULT_LEARNING_PROGRESS_PATH = Path("data") / "learning_progress.v0.1.jsonl"
LEARNING_PATH_PATH = Path("data") / "learning_path.v0.1.json"
PRODUCT_METRICS_PATH = Path("data") / "product_metrics.v0.1.json"
PHASE13_REPORT_PATH = Path("data") / "phase13_productization_report.v0.1.json"

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
RISK_INCIDENT_TYPES = {
    "high_risk_leak",
    "deterministic_promise",
    "professional_without_evidence",
    "copyright_complaint",
    "copyright_blocked_visible",
    "realtime_tool_bypass",
}


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(root: str | Path | None, path: Path) -> Any:
    return json.loads((_root(root) / path).read_text(encoding="utf-8"))


def _visitor_profile_path(root: str | Path | None = None, profile_path: str | Path | None = None) -> Path:
    if profile_path is not None:
        return Path(profile_path)
    env_path = os.getenv("LIUREN_VISITOR_PROFILE_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_VISITOR_PROFILE_PATH


def _learning_progress_path(root: str | Path | None = None, progress_path: str | Path | None = None) -> Path:
    if progress_path is not None:
        return Path(progress_path)
    env_path = os.getenv("LIUREN_LEARNING_PROGRESS_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_LEARNING_PROGRESS_PATH


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


def load_productization_config(root: str | Path | None = None) -> dict:
    return _read_json(root, PRODUCTIZATION_CONFIG_PATH)


def load_learning_path(root: str | Path | None = None) -> dict:
    return _read_json(root, LEARNING_PATH_PATH)


def _sanitize_visitor_profile(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "profile_id",
        "visitor_id",
        "nickname",
        "mode_preference",
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
    record.setdefault("mode_preference", "plain")
    record.setdefault("source", "productization_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["profile_id"] = str(
        record.get("profile_id")
        or f"visitor_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}"
    )
    return record


def record_visitor_profile(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    profile_path: str | Path | None = None,
) -> dict:
    record = _sanitize_visitor_profile(payload)
    _append_jsonl(_visitor_profile_path(root, profile_path), record)
    return record


def load_visitor_profiles(root: str | Path | None = None, profile_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_visitor_profile_path(root, profile_path))


def _sanitize_learning_progress(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "progress_id",
        "visitor_id",
        "node_id",
        "event_type",
        "status",
        "mode",
        "chart_id",
        "source",
        "reflection_note",
        "content_id",
    }
    lower_keys = {str(key).lower() for key in payload.keys()}
    record = {key: _clean_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    dropped = lower_keys & SENSITIVE_KEYS
    if dropped:
        record["dropped_sensitive_field_count"] = len(dropped)
    record.setdefault("visitor_id", "anonymous")
    record.setdefault("event_type", "learning_progress")
    record.setdefault("status", "started")
    record.setdefault("mode", "plain")
    record.setdefault("source", "productization_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["progress_id"] = str(
        record.get("progress_id")
        or f"progress_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}"
    )
    return record


def record_learning_progress(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    progress_path: str | Path | None = None,
) -> dict:
    record = _sanitize_learning_progress(payload)
    _append_jsonl(_learning_progress_path(root, progress_path), record)
    return record


def load_learning_progress(root: str | Path | None = None, progress_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_learning_progress_path(root, progress_path))


def _risk_incident_count(public_metrics: Mapping[str, Any]) -> int:
    incident_distribution = dict(public_metrics.get("incident_distribution") or {})
    return sum(int(incident_distribution.get(name, 0) or 0) for name in RISK_INCIDENT_TYPES)


def build_productization_gate(
    root: str | Path | None = None,
    public_status: Mapping[str, Any] | None = None,
    public_metrics: Mapping[str, Any] | None = None,
) -> dict:
    from .public_launch import build_public_metrics, build_public_status

    config = load_productization_config(root)
    status = dict(public_status or build_public_status(root))
    metrics = dict(public_metrics or build_public_metrics(root))
    blocked_reasons: list[str] = []
    pause_reason = ""
    launch_status = str(status.get("launch_status") or status.get("public_launch_status") or "blocked")
    critical_incidents = int(status.get("critical_incident_count", 0) or 0) + int(metrics.get("critical_incident_count", 0) or 0)

    if launch_status == "paused" or critical_incidents or _risk_incident_count(metrics):
        gate_status = "paused"
        pause_reason = "public_risk_event"
        blocked_reasons.append("critical_public_incident")
        blocked_reasons.extend(str(reason) for reason in status.get("blocked_reasons", []) if reason)
    elif launch_status not in {"preview", "live"}:
        gate_status = "blocked"
        blocked_reasons.append("public_mvp_not_active")
        blocked_reasons.extend(str(reason) for reason in status.get("blocked_reasons", []) if reason)
    elif not config.get("experiment_enabled", True):
        gate_status = "blocked"
        blocked_reasons.append("productization_experiment_disabled")
    else:
        gate_status = "experiment"

    blocked_reasons = list(dict.fromkeys(blocked_reasons))
    return {
        "gate_id": "productization_gate.v0.1",
        "generated_at": _utc_now(),
        "gate_status": gate_status,
        "pause_reason": pause_reason,
        "blocked_reasons": blocked_reasons,
        "public_launch_status": launch_status,
        "public_status_id": status.get("status_id", "public_status.v0.1"),
        "public_metrics_id": metrics.get("metrics_id", "public_metrics.v0.1"),
        "enabled_experiments": config.get("enabled_experiments", []) if gate_status == "experiment" else [],
        "next_step": "run_productization_experiment" if gate_status == "experiment" else "return_to_public_launch_fix",
    }


def build_product_metrics(
    root: str | Path | None = None,
    profile_path: str | Path | None = None,
    progress_path: str | Path | None = None,
    public_metrics: Mapping[str, Any] | None = None,
) -> dict:
    from .public_launch import build_public_metrics

    profiles = load_visitor_profiles(root, profile_path)
    progress = load_learning_progress(root, progress_path)
    public = dict(public_metrics or build_public_metrics(root))
    visitors = {str(record.get("visitor_id")) for record in profiles + progress if record.get("visitor_id")}
    event_counts = Counter(str(record.get("event_type", "learning_progress")) for record in progress)
    status_counts = Counter(str(record.get("status", "unknown")) for record in progress)
    mode_counts = Counter(str(record.get("mode", "unknown")) for record in progress if record.get("mode"))
    visitor_events: defaultdict[str, int] = defaultdict(int)
    for record in profiles + progress:
        visitor_id = str(record.get("visitor_id") or "")
        if visitor_id:
            visitor_events[visitor_id] += 1
    return {
        "metrics_id": "product_metrics.v0.1",
        "generated_at": _utc_now(),
        "visitor_count": len(visitors),
        "profile_count": len(profiles),
        "learning_progress_count": len(progress),
        "completed_node_count": int(status_counts.get("completed", 0)),
        "returning_visitor_count": sum(1 for count in visitor_events.values() if count >= 2),
        "pdf_report_draft_count": int(event_counts.get("pdf_report_generated", 0)),
        "content_click_count": int(event_counts.get("content_clicked", 0)),
        "reflection_note_count": sum(1 for record in progress if record.get("reflection_note")),
        "delete_request_count": sum(1 for record in profiles if record.get("delete_request")),
        "mode_distribution": dict(mode_counts),
        "event_distribution": dict(event_counts),
        "public_metrics": public,
    }


def build_phase13_report(
    root: str | Path | None = None,
    profile_path: str | Path | None = None,
    progress_path: str | Path | None = None,
    public_status: Mapping[str, Any] | None = None,
    public_metrics: Mapping[str, Any] | None = None,
) -> dict:
    gate = build_productization_gate(root, public_status=public_status, public_metrics=public_metrics)
    metrics = build_product_metrics(root, profile_path, progress_path, public_metrics=public_metrics)
    if gate.get("gate_status") == "experiment":
        decision = "continue_productization_experiment"
    elif gate.get("gate_status") == "paused":
        decision = "pause_and_fix_productization"
    else:
        decision = "do_not_start_productization"
    return {
        "report_id": "phase13_productization_report.v0.1",
        "generated_at": _utc_now(),
        "productization_gate": gate,
        "product_metrics": metrics,
        "decision": decision,
        "next_step": "phase14_commercialization_experiment" if decision == "continue_productization_experiment" else "return_to_phase12_fix",
        "blocked_review_list": gate.get("blocked_reasons", []),
    }
