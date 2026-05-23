from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MONETIZATION_CONFIG_PATH = Path("data") / "monetization_config.v0.1.json"
MONETIZATION_GATE_PATH = Path("data") / "monetization_gate.v0.1.json"
OFFER_CATALOG_PATH = Path("data") / "offer_catalog.v0.1.json"
DEFAULT_EVENTS_PATH = Path("data") / "monetization_events.v0.1.jsonl"
DEFAULT_LEADS_PATH = Path("data") / "business_leads.v0.1.jsonl"
MONETIZATION_METRICS_PATH = Path("data") / "monetization_metrics.v0.1.json"
PHASE14_REPORT_PATH = Path("data") / "phase14_monetization_report.v0.1.json"

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


def _events_path(root: str | Path | None = None, events_path: str | Path | None = None) -> Path:
    if events_path is not None:
        return Path(events_path)
    env_path = os.getenv("LIUREN_MONETIZATION_EVENTS_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_EVENTS_PATH


def _leads_path(root: str | Path | None = None, leads_path: str | Path | None = None) -> Path:
    if leads_path is not None:
        return Path(leads_path)
    env_path = os.getenv("LIUREN_BUSINESS_LEADS_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_LEADS_PATH


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


def load_monetization_config(root: str | Path | None = None) -> dict:
    return _read_json(root, MONETIZATION_CONFIG_PATH)


def load_offer_catalog(root: str | Path | None = None) -> dict:
    return _read_json(root, OFFER_CATALOG_PATH)


def _sanitize_event(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "event_id",
        "visitor_id",
        "event_type",
        "offer_id",
        "source",
        "mode",
        "note",
        "delete_request",
    }
    lower_keys = {str(key).lower() for key in payload.keys()}
    record = {key: _clean_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    dropped = lower_keys & SENSITIVE_KEYS
    if dropped:
        record["dropped_sensitive_field_count"] = len(dropped)
    record.setdefault("visitor_id", "anonymous")
    record.setdefault("event_type", "offer_click")
    record.setdefault("source", "monetization_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["event_id"] = str(
        record.get("event_id")
        or f"monetization_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}"
    )
    return record


def record_monetization_event(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    events_path: str | Path | None = None,
) -> dict:
    record = _sanitize_event(payload)
    _append_jsonl(_events_path(root, events_path), record)
    return record


def load_monetization_events(root: str | Path | None = None, events_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_events_path(root, events_path))


def _sanitize_lead(payload: Mapping[str, Any]) -> dict:
    allowed_keys = {
        "lead_id",
        "visitor_id",
        "contact_nickname",
        "channel",
        "need_summary",
        "source",
        "offer_id",
        "delete_request",
    }
    lower_keys = {str(key).lower() for key in payload.keys()}
    record = {key: _clean_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    dropped = lower_keys & SENSITIVE_KEYS
    if dropped:
        record["dropped_sensitive_field_count"] = len(dropped)
    record.setdefault("visitor_id", "anonymous")
    record.setdefault("channel", "web")
    record.setdefault("source", "monetization_api")
    record["timestamp"] = str(payload.get("timestamp") or _utc_now())
    record["lead_id"] = str(
        record.get("lead_id")
        or f"business_lead_{abs(hash(json.dumps(record, ensure_ascii=False, sort_keys=True))) % 10_000_000:07d}"
    )
    return record


def record_business_lead(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    leads_path: str | Path | None = None,
) -> dict:
    record = _sanitize_lead(payload)
    _append_jsonl(_leads_path(root, leads_path), record)
    return record


def load_business_leads(root: str | Path | None = None, leads_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_leads_path(root, leads_path))


def _copyright_blocked_visible(copyright_review: Mapping[str, Any]) -> bool:
    for item in copyright_review.get("items", []):
        if item.get("visible_in_product") and item.get("beta_status") == "blocked":
            return True
        if item.get("visible_in_product") and item.get("status") == "blocked":
            return True
    return False


def _risk_incident_count(product_metrics: Mapping[str, Any]) -> int:
    public_metrics = dict(product_metrics.get("public_metrics") or {})
    incident_distribution = dict(public_metrics.get("incident_distribution") or {})
    return int(public_metrics.get("critical_incident_count", 0) or 0) + sum(
        int(incident_distribution.get(name, 0) or 0) for name in RISK_INCIDENT_TYPES
    )


def build_monetization_gate(
    root: str | Path | None = None,
    productization_gate: Mapping[str, Any] | None = None,
    product_metrics: Mapping[str, Any] | None = None,
    copyright_review: Mapping[str, Any] | None = None,
) -> dict:
    from .productization import build_product_metrics, build_productization_gate
    from .safety_review import load_copyright_review

    config = load_monetization_config(root)
    product_gate = dict(productization_gate or build_productization_gate(root))
    metrics = dict(product_metrics or build_product_metrics(root))
    copyright_state = dict(copyright_review or load_copyright_review(root))
    blocked_reasons: list[str] = []
    pause_reason = ""
    risk_count = _risk_incident_count(metrics)

    if risk_count or _copyright_blocked_visible(copyright_state):
        gate_status = "paused"
        pause_reason = "risk_or_copyright_block"
        if risk_count:
            blocked_reasons.append("critical_public_incident")
        if _copyright_blocked_visible(copyright_state):
            blocked_reasons.append("copyright_blocked_visible")
    elif product_gate.get("gate_status") != "experiment":
        gate_status = "blocked"
        blocked_reasons.append("productization_not_active")
        blocked_reasons.extend(str(reason) for reason in product_gate.get("blocked_reasons", []) if reason)
    elif not config.get("experiment_enabled", True):
        gate_status = "blocked"
        blocked_reasons.append("monetization_experiment_disabled")
    else:
        gate_status = "experiment"

    blocked_reasons = list(dict.fromkeys(blocked_reasons))
    return {
        "gate_id": "monetization_gate.v0.1",
        "generated_at": _utc_now(),
        "gate_status": gate_status,
        "pause_reason": pause_reason,
        "blocked_reasons": blocked_reasons,
        "productization_gate_status": product_gate.get("gate_status"),
        "enabled_experiments": config.get("enabled_experiments", []) if gate_status == "experiment" else [],
        "next_step": "run_monetization_interest_experiment" if gate_status == "experiment" else "return_to_productization_fix",
    }


def build_monetization_metrics(
    root: str | Path | None = None,
    events_path: str | Path | None = None,
    leads_path: str | Path | None = None,
    product_metrics: Mapping[str, Any] | None = None,
) -> dict:
    from .productization import build_product_metrics

    events = load_monetization_events(root, events_path)
    leads = load_business_leads(root, leads_path)
    product = dict(product_metrics or build_product_metrics(root))
    event_counts = Counter(str(event.get("event_type", "unknown")) for event in events)
    offer_counts = Counter(str(event.get("offer_id", "unknown")) for event in events if event.get("offer_id"))
    visitor_counts: defaultdict[str, int] = defaultdict(int)
    for record in events + leads:
        visitor_id = str(record.get("visitor_id") or "")
        if visitor_id:
            visitor_counts[visitor_id] += 1
    interest_summary = {
        "member_interest": int(event_counts.get("member_interest", 0)),
        "course_interest": int(event_counts.get("course_interest", 0)),
        "business_interest": int(event_counts.get("business_interest", 0)),
        "ip_interest": int(event_counts.get("ip_interest", 0)),
        "pricing_view": int(event_counts.get("pricing_view", 0)),
        "offer_click": int(event_counts.get("offer_click", 0)),
        "business_leads": len(leads),
    }
    return {
        "metrics_id": "monetization_metrics.v0.1",
        "generated_at": _utc_now(),
        "event_count": len(events),
        "business_lead_count": len(leads),
        "unique_visitor_count": len(visitor_counts),
        "returning_visitor_count": sum(1 for count in visitor_counts.values() if count >= 2),
        "member_interest_count": interest_summary["member_interest"],
        "course_interest_count": interest_summary["course_interest"],
        "business_interest_count": interest_summary["business_interest"],
        "ip_interest_count": interest_summary["ip_interest"],
        "pricing_view_count": interest_summary["pricing_view"],
        "offer_click_count": interest_summary["offer_click"],
        "delete_request_count": sum(1 for record in events + leads if record.get("delete_request")),
        "event_distribution": dict(event_counts),
        "offer_distribution": dict(offer_counts),
        "interest_summary": interest_summary,
        "product_metrics": product,
    }


def build_phase14_report(
    root: str | Path | None = None,
    events_path: str | Path | None = None,
    leads_path: str | Path | None = None,
    productization_gate: Mapping[str, Any] | None = None,
    product_metrics: Mapping[str, Any] | None = None,
    copyright_review: Mapping[str, Any] | None = None,
) -> dict:
    metrics = build_monetization_metrics(root, events_path, leads_path, product_metrics)
    gate = build_monetization_gate(
        root,
        productization_gate=productization_gate,
        product_metrics=product_metrics or metrics.get("product_metrics", {}),
        copyright_review=copyright_review,
    )
    catalog = load_offer_catalog(root)
    if gate.get("gate_status") == "experiment":
        decision = "continue_monetization_experiment"
    elif gate.get("gate_status") == "paused":
        decision = "pause_and_fix_monetization"
    else:
        decision = "do_not_start_monetization"
    return {
        "report_id": "phase14_monetization_report.v0.1",
        "generated_at": _utc_now(),
        "monetization_gate": gate,
        "offer_catalog": {
            "catalog_id": catalog.get("catalog_id", "offer_catalog.v0.1"),
            "offer_count": len(catalog.get("offers", [])),
        },
        "monetization_metrics": metrics,
        "interest_summary": metrics["interest_summary"],
        "decision": decision,
        "next_step": "phase15_payment_membership_preparation" if decision == "continue_monetization_experiment" else "return_to_phase13_or_safety_fix",
        "blocked_reasons": gate.get("blocked_reasons", []),
    }
