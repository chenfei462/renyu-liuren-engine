from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


EXPERT_WORKFLOW_PATH = Path("data") / "expert_review_workflow.v0.1.json"
CANARY_TESTERS_PATH = Path("data") / "canary_testers.v0.1.json"
CONTENT_CALENDAR_PATH = Path("data") / "content_calendar.v0.1.json"
DEFAULT_GROWTH_EVENTS_PATH = Path("data") / "growth_events.v0.1.jsonl"
GROWTH_METRICS_PATH = Path("data") / "growth_metrics.v0.1.json"
GROWTH_REPORT_PATH = Path("data") / "phase10_growth_report.v0.1.json"

BLOCKING_RULES = {"biyong", "shehai", "yaoke", "maoxing", "bazhuan", "bieze", "fuyin", "fanyin"}
CANARY_DECISIONS = {"approved_for_canary", "research_only"}
ALL_DECISIONS = CANARY_DECISIONS | {"blocked_until_reworked"}
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


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _expert_workflow_path(root: str | Path | None = None) -> Path:
    env_path = os.getenv("LIUREN_EXPERT_WORKFLOW_PATH")
    return Path(env_path) if env_path else _root(root) / EXPERT_WORKFLOW_PATH


def _canary_config_path(root: str | Path | None = None) -> Path:
    env_path = os.getenv("LIUREN_CANARY_TESTERS_PATH")
    return Path(env_path) if env_path else _root(root) / CANARY_TESTERS_PATH


def _growth_events_path(root: str | Path | None = None, growth_events_path: str | Path | None = None) -> Path:
    if growth_events_path is not None:
        return Path(growth_events_path)
    env_path = os.getenv("LIUREN_GROWTH_EVENTS_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_GROWTH_EVENTS_PATH


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


def load_expert_review_workflow(root: str | Path | None = None) -> dict:
    return json.loads(_expert_workflow_path(root).read_text(encoding="utf-8"))


def _blocking_review_tasks(workflow: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [task for task in workflow.get("tasks", []) if str(task.get("rule_id", "")) in BLOCKING_RULES]


def build_review_gate(root: str | Path | None = None, expert_workflow: Mapping[str, Any] | None = None) -> dict:
    workflow = dict(expert_workflow or load_expert_review_workflow(root))
    tasks = _blocking_review_tasks(workflow)
    covered_rules = {str(task.get("rule_id")) for task in tasks}
    missing_rules = sorted(BLOCKING_RULES - covered_rules)
    blocked_rules: list[str] = []
    research_only_rules: list[str] = []
    approved_rules: list[str] = []

    for task in tasks:
        rule_id = str(task.get("rule_id", ""))
        decision = str(task.get("decision", ""))
        allow_canary = bool(task.get("allow_canary"))
        if decision == "approved_for_canary" and allow_canary:
            approved_rules.append(rule_id)
        elif decision == "research_only" and allow_canary:
            research_only_rules.append(rule_id)
        else:
            blocked_rules.append(rule_id)

    blocked_rules = sorted(set(blocked_rules + missing_rules))
    blocked_reasons = ["expert_review_pending"] if blocked_rules else []
    return {
        "gate_id": "canary_gate.v0.1",
        "workflow_id": workflow.get("workflow_id", "expert_review_workflow.v0.1"),
        "canary_allowed": not blocked_rules,
        "blocked_reasons": blocked_reasons,
        "blocked_rules": blocked_rules,
        "approved_rules": sorted(set(approved_rules)),
        "research_only_rules": sorted(set(research_only_rules)),
        "required_rules": sorted(BLOCKING_RULES),
        "task_count": len(tasks),
        "missing_rules": missing_rules,
    }


def update_expert_review_task(payload: Mapping[str, Any], root: str | Path | None = None) -> dict:
    path = _expert_workflow_path(root)
    workflow = json.loads(path.read_text(encoding="utf-8"))
    task_id = str(payload.get("task_id") or "")
    rule_id = str(payload.get("rule_id") or "")
    decision = str(payload.get("decision") or "")
    if decision and decision not in ALL_DECISIONS:
        raise ValueError(f"unsupported expert review decision: {decision}")

    target: dict[str, Any] | None = None
    for task in workflow.get("tasks", []):
        if (task_id and task.get("task_id") == task_id) or (rule_id and task.get("rule_id") == rule_id):
            target = task
            break
    if target is None:
        raise KeyError("expert review task not found")

    for key in ["expert_opinion", "processing_result", "status", "reviewer", "notes"]:
        if key in payload:
            target[key] = _clean_scalar(payload[key])
    if decision:
        target["decision"] = decision
        target["allow_canary"] = bool(payload.get("allow_canary", decision in CANARY_DECISIONS))
    elif "allow_canary" in payload:
        target["allow_canary"] = bool(payload["allow_canary"])
    target["updated_at"] = _utc_now()
    _write_json(path, workflow)
    return {"updated": True, "task": target, "canary_gate": build_review_gate(expert_workflow=workflow)}


def load_canary_config(root: str | Path | None = None) -> dict:
    return json.loads(_canary_config_path(root).read_text(encoding="utf-8"))


def _active_tester_ids(config: Mapping[str, Any]) -> set[str]:
    return {
        str(tester.get("tester_id"))
        for tester in config.get("testers", [])
        if tester.get("status") == "active" and tester.get("tester_id")
    }


def _active_invite_codes(config: Mapping[str, Any]) -> set[str]:
    return {
        str(item.get("code"))
        for item in config.get("invite_codes", [])
        if item.get("status") == "active" and item.get("code")
    }


def validate_canary_access(
    payload: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
    root: str | Path | None = None,
) -> dict:
    canary_config = dict(config or load_canary_config(root))
    tester_id = str(payload.get("tester_id") or "").strip()
    invite_code = str(payload.get("invite_code") or "").strip()
    valid_tester = tester_id in _active_tester_ids(canary_config)
    valid_invite = invite_code in _active_invite_codes(canary_config)
    allowed = valid_tester or valid_invite
    return {
        "validation_id": "canary_validate.v0.1",
        "canary_id": canary_config.get("canary_id", "canary_testers.v0.1"),
        "allowed": allowed,
        "tester_id": tester_id if valid_tester else "",
        "invite_code_accepted": valid_invite,
        "blocked_reasons": [] if allowed else ["invalid_canary_credentials"],
        "notice": canary_config.get("notice", ""),
    }


def load_content_calendar(root: str | Path | None = None) -> dict:
    return _read_json(root, CONTENT_CALENDAR_PATH)


def _sanitize_growth_event(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "tester_id",
        "invite_code",
        "event_type",
        "mode",
        "content_id",
        "chart_id",
        "source",
        "note",
        "category",
        "feedback_token",
        "task_id",
        "channel",
    }
    lower_keys = {str(key).lower() for key in payload.keys()}
    record = {key: _clean_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    dropped = sorted(lower_keys & SENSITIVE_KEYS)
    if dropped:
        record["dropped_sensitive_field_count"] = len(dropped)
    record.setdefault("tester_id", "anonymous")
    record.setdefault("event_type", "growth_event")
    record.setdefault("mode", "plain")
    record.setdefault("source", "local_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["event_id"] = str(
        payload.get("event_id")
        or f"growth_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}"
    )
    return record


def record_growth_event(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    growth_events_path: str | Path | None = None,
) -> dict:
    record = _sanitize_growth_event(payload)
    path = _growth_events_path(root, growth_events_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def load_growth_events(root: str | Path | None = None, growth_events_path: str | Path | None = None) -> list[dict]:
    path = _growth_events_path(root, growth_events_path)
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


def build_share_report_metrics(event_counts: Mapping[str, int | float]) -> dict[str, Any]:
    generated_count = int(event_counts.get("share_report_generated", 0) or 0)
    user_reach_count = int(event_counts.get("share_report_user_reached", 0) or 0)
    return {
        "share_report_count": generated_count,
        "share_report_generated_count": generated_count,
        "share_report_user_reach_count": user_reach_count,
        "share_report_metrics": {
            "generated_count": generated_count,
            "user_reach_count": user_reach_count,
            "generated_event_type": "share_report_generated",
            "user_reach_event_type": "share_report_user_reached",
            "legacy_count_field": "share_report_count",
            "legacy_count_semantics": "generated_count",
            "tracking_status": "generated_and_reach" if user_reach_count else "generated_only",
        },
    }


def build_growth_metrics(root: str | Path | None = None, growth_events_path: str | Path | None = None) -> dict:
    events = load_growth_events(root, growth_events_path)
    event_counts = Counter(str(event.get("event_type", "unknown")) for event in events)
    mode_counts = Counter(str(event.get("mode", "unknown")) for event in events)
    tester_event_counts: defaultdict[str, int] = defaultdict(int)
    for event in events:
        tester_id = str(event.get("tester_id") or "")
        if tester_id and tester_id != "anonymous":
            tester_event_counts[tester_id] += 1
    metrics = {
        "metrics_id": "growth_metrics.v0.1",
        "generated_at": _utc_now(),
        "event_count": len(events),
        "unique_tester_count": len(tester_event_counts),
        "returning_tester_count": sum(1 for count in tester_event_counts.values() if count >= 2),
        "story_mode_count": int(mode_counts.get("story", 0)),
        "mentor_mode_count": int(mode_counts.get("mentor", 0)),
        "learning_card_click_count": int(event_counts.get("learning_card_click", 0)),
        "feedback_submit_count": int(event_counts.get("feedback_submitted", 0)),
        "member_interest_count": int(event_counts.get("member_interest", 0)),
        "course_interest_count": int(event_counts.get("course_interest", 0)),
        "business_interest_count": int(event_counts.get("business_interest", 0)),
        "event_distribution": dict(event_counts),
        "mode_distribution": dict(mode_counts),
    }
    metrics.update(build_share_report_metrics(event_counts))
    return metrics


def build_growth_report(root: str | Path | None = None, growth_events_path: str | Path | None = None) -> dict:
    metrics = build_growth_metrics(root, growth_events_path)
    review_gate = build_review_gate(root)
    calendar = load_content_calendar(root)
    if review_gate["blocked_reasons"]:
        recommendation = "return_to_expert_review"
    elif metrics["event_count"] < 20:
        recommendation = "continue_canary_learning"
    else:
        recommendation = "prepare_public_release_review"
    return {
        "report_id": "phase10_growth_report.v0.1",
        "generated_at": _utc_now(),
        "review_gate": review_gate,
        "growth_metrics": metrics,
        "content_calendar": {
            "calendar_id": calendar.get("calendar_id", "content_calendar.v0.1"),
            "item_count": len(calendar.get("items", [])),
            "active_columns": sorted({str(item.get("column")) for item in calendar.get("items", [])}),
        },
        "recommendation": recommendation,
    }
