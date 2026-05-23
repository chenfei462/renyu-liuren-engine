from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


PAYMENT_CONFIG_PATH = Path("data") / "payment_config.v0.1.json"
PAYMENT_GATE_PATH = Path("data") / "payment_readiness_gate.v0.1.json"
MEMBERSHIP_TIERS_PATH = Path("data") / "membership_tiers.v0.1.json"
DEFAULT_ORDERS_PATH = Path("data") / "sandbox_orders.v0.1.jsonl"
DEFAULT_EVENTS_PATH = Path("data") / "payment_events.v0.1.jsonl"
DEFAULT_REFUNDS_PATH = Path("data") / "refund_cases.v0.1.jsonl"
PAYMENT_METRICS_PATH = Path("data") / "payment_metrics.v0.1.json"
PHASE15_REPORT_PATH = Path("data") / "phase15_payment_readiness_report.v0.1.json"

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
    "payment_secret",
    "provider_secret",
    "card_number",
    "cvv",
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
FORBIDDEN_COPY_TERMS = {"准确率", "保证", "包赢", "必赚", "胜诉", "确诊", "用药", "必然", "一定"}
ALLOWED_TRANSITIONS = {
    "pending_payment": {"paid_sandbox", "failed", "canceled"},
    "paid_sandbox": {"refunded"},
    "created": {"pending_payment", "canceled"},
}


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(root: str | Path | None, path: Path) -> Any:
    return json.loads((_root(root) / path).read_text(encoding="utf-8"))


def _orders_path(root: str | Path | None = None, orders_path: str | Path | None = None) -> Path:
    if orders_path is not None:
        return Path(orders_path)
    env_path = os.getenv("LIUREN_PAYMENT_ORDERS_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_ORDERS_PATH


def _events_path(root: str | Path | None = None, events_path: str | Path | None = None) -> Path:
    if events_path is not None:
        return Path(events_path)
    env_path = os.getenv("LIUREN_PAYMENT_EVENTS_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_EVENTS_PATH


def _refunds_path(root: str | Path | None = None, refunds_path: str | Path | None = None) -> Path:
    if refunds_path is not None:
        return Path(refunds_path)
    env_path = os.getenv("LIUREN_REFUND_CASES_PATH")
    return Path(env_path) if env_path else _root(root) / DEFAULT_REFUNDS_PATH


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


def load_payment_config(root: str | Path | None = None) -> dict:
    return _read_json(root, PAYMENT_CONFIG_PATH)


def load_membership_tiers(root: str | Path | None = None) -> dict:
    return _read_json(root, MEMBERSHIP_TIERS_PATH)


def load_sandbox_orders(root: str | Path | None = None, orders_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_orders_path(root, orders_path))


def load_payment_events(root: str | Path | None = None, events_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_events_path(root, events_path))


def load_refund_cases(root: str | Path | None = None, refunds_path: str | Path | None = None) -> list[dict]:
    return _load_jsonl(_refunds_path(root, refunds_path))


def _clean_record(payload: Mapping[str, Any], allowed_keys: set[str]) -> dict:
    lower_keys = {str(key).lower() for key in payload.keys()}
    record = {key: _clean_scalar(payload.get(key)) for key in allowed_keys if key in payload}
    dropped = lower_keys & SENSITIVE_KEYS
    if dropped:
        record["dropped_sensitive_field_count"] = len(dropped)
    return record


def _record_id(prefix: str, record: Mapping[str, Any]) -> str:
    rendered = json.dumps(record, ensure_ascii=False, sort_keys=True)
    return f"{prefix}_{abs(hash(rendered)) % 10_000_000:07d}"


def _append_payment_event(
    event_type: str,
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    events_path: str | Path | None = None,
) -> dict:
    allowed_keys = {
        "event_id",
        "order_id",
        "visitor_id",
        "tier_id",
        "event_type",
        "provider",
        "order_status",
        "reason",
        "source",
        "note",
        "delete_request",
    }
    event = _clean_record(payload, allowed_keys)
    event["event_type"] = event_type
    event.setdefault("provider", "mock_sandbox")
    event.setdefault("source", "payment_api")
    event["timestamp"] = str(payload.get("timestamp") or _utc_now())
    event["event_id"] = str(event.get("event_id") or _record_id("payment_event", event))
    _append_jsonl(_events_path(root, events_path), event)
    return event


def _append_order(
    payload: Mapping[str, Any],
    order_status: str,
    root: str | Path | None = None,
    orders_path: str | Path | None = None,
) -> dict:
    allowed_keys = {
        "order_id",
        "visitor_id",
        "tier_id",
        "order_status",
        "provider",
        "currency",
        "amount_cents",
        "source",
        "note",
        "delete_request",
    }
    order = _clean_record(payload, allowed_keys)
    order["order_status"] = order_status
    order.setdefault("visitor_id", "anonymous")
    order.setdefault("tier_id", "tier-free-v0")
    order.setdefault("provider", "mock_sandbox")
    order.setdefault("currency", "CNY")
    order.setdefault("amount_cents", 0)
    order.setdefault("source", "payment_api")
    order["timestamp"] = str(payload.get("timestamp") or _utc_now())
    order["order_id"] = str(order.get("order_id") or _record_id("sandbox_order", order))
    _append_jsonl(_orders_path(root, orders_path), order)
    return order


def _latest_order(order_id: str, root: str | Path | None = None, orders_path: str | Path | None = None) -> dict | None:
    latest: dict | None = None
    for order in load_sandbox_orders(root, orders_path):
        if order.get("order_id") == order_id:
            latest = order
    return latest


def _blocked_order(order_id: str, reason: str) -> dict:
    return {
        "order_id": order_id,
        "order_status": "blocked",
        "provider": "mock_sandbox",
        "reason": reason,
        "timestamp": _utc_now(),
    }


def _transition_order(
    order_id: str,
    next_status: str,
    event_type: str,
    reason: str = "",
    root: str | Path | None = None,
    orders_path: str | Path | None = None,
    events_path: str | Path | None = None,
) -> dict:
    current = _latest_order(order_id, root, orders_path)
    if not current:
        blocked = _blocked_order(order_id, "order_not_found")
        event = _append_payment_event(
            "payment_blocked",
            {"order_id": order_id, "order_status": "blocked", "reason": "order_not_found"},
            root,
            events_path,
        )
        return {"order": blocked, "event": event}
    current_status = str(current.get("order_status", "unknown"))
    if next_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
        blocked = _blocked_order(order_id, f"invalid_transition:{current_status}->{next_status}")
        event = _append_payment_event(
            "payment_blocked",
            {"order_id": order_id, "order_status": "blocked", "reason": blocked["reason"]},
            root,
            events_path,
        )
        return {"order": blocked, "event": event}
    order_payload = dict(current)
    if reason:
        order_payload["reason"] = reason
    order = _append_order(order_payload, next_status, root, orders_path)
    event = _append_payment_event(event_type, {**order, "reason": reason}, root, events_path)
    return {"order": order, "event": event}


def create_sandbox_checkout(
    payload: Mapping[str, Any],
    root: str | Path | None = None,
    orders_path: str | Path | None = None,
    events_path: str | Path | None = None,
) -> dict:
    order = _append_order(payload, "pending_payment", root, orders_path)
    event = _append_payment_event("checkout_started", order, root, events_path)
    return {"order": order, "event": event}


def confirm_sandbox_payment(
    order_id: str,
    outcome: str = "success",
    root: str | Path | None = None,
    orders_path: str | Path | None = None,
    events_path: str | Path | None = None,
) -> dict:
    if outcome == "success":
        return _transition_order(order_id, "paid_sandbox", "sandbox_paid", root=root, orders_path=orders_path, events_path=events_path)
    return _transition_order(order_id, "failed", "payment_failed", root=root, orders_path=orders_path, events_path=events_path)


def cancel_sandbox_order(
    order_id: str,
    reason: str = "",
    root: str | Path | None = None,
    orders_path: str | Path | None = None,
    events_path: str | Path | None = None,
) -> dict:
    return _transition_order(order_id, "canceled", "subscription_canceled", reason, root, orders_path, events_path)


def refund_sandbox_order(
    order_id: str,
    reason: str = "",
    root: str | Path | None = None,
    orders_path: str | Path | None = None,
    events_path: str | Path | None = None,
    refunds_path: str | Path | None = None,
) -> dict:
    result = _transition_order(order_id, "refunded", "refund_completed", reason, root, orders_path, events_path)
    if result["order"].get("order_status") == "refunded":
        refund = {
            "refund_id": _record_id("refund_case", result["order"]),
            "order_id": order_id,
            "visitor_id": result["order"].get("visitor_id"),
            "tier_id": result["order"].get("tier_id"),
            "reason": _clean_scalar(reason),
            "provider": "mock_sandbox",
            "status": "refund_completed",
            "timestamp": _utc_now(),
        }
        _append_jsonl(_refunds_path(root, refunds_path), refund)
        result["refund"] = refund
    return result


def _copyright_blocked_visible(copyright_review: Mapping[str, Any]) -> bool:
    for item in copyright_review.get("items", []):
        if item.get("visible_in_product") and item.get("beta_status") == "blocked":
            return True
        if item.get("visible_in_product") and item.get("status") == "blocked":
            return True
    return False


def _risk_incident_count(metrics: Mapping[str, Any]) -> int:
    product_metrics = dict(metrics.get("product_metrics") or {})
    public_metrics = dict(product_metrics.get("public_metrics") or {})
    incident_distribution = dict(public_metrics.get("incident_distribution") or {})
    return int(public_metrics.get("critical_incident_count", 0) or 0) + sum(
        int(incident_distribution.get(name, 0) or 0) for name in RISK_INCIDENT_TYPES
    )


def _forbidden_terms_in_payment_copy(root: str | Path | None = None) -> list[str]:
    terms: list[str] = []
    for path in [PAYMENT_CONFIG_PATH, MEMBERSHIP_TIERS_PATH]:
        target = _root(root) / path
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        for term in FORBIDDEN_COPY_TERMS:
            if term in text and term not in terms:
                terms.append(term)
    return terms


def _interest_thresholds_met(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> bool:
    thresholds = dict(config.get("minimum_interest_thresholds") or {})
    for key, minimum in thresholds.items():
        if int(metrics.get(key, 0) or 0) < int(minimum):
            return False
    return True


def build_payment_readiness_gate(
    root: str | Path | None = None,
    monetization_gate: Mapping[str, Any] | None = None,
    monetization_metrics: Mapping[str, Any] | None = None,
    copyright_review: Mapping[str, Any] | None = None,
    forbidden_terms_found: list[str] | None = None,
) -> dict:
    from .monetization import build_monetization_gate, build_monetization_metrics
    from .safety_review import load_copyright_review

    config = load_payment_config(root)
    money_gate = dict(monetization_gate or build_monetization_gate(root))
    metrics = dict(monetization_metrics or build_monetization_metrics(root))
    copyright_state = dict(copyright_review or load_copyright_review(root))
    forbidden_terms = list(forbidden_terms_found if forbidden_terms_found is not None else _forbidden_terms_in_payment_copy(root))
    blocked_reasons: list[str] = []
    pause_reason = ""

    if _risk_incident_count(metrics) or _copyright_blocked_visible(copyright_state) or forbidden_terms:
        gate_status = "paused"
        pause_reason = "risk_or_compliance_block"
        if _risk_incident_count(metrics):
            blocked_reasons.append("critical_public_incident")
        if _copyright_blocked_visible(copyright_state):
            blocked_reasons.append("copyright_blocked_visible")
        if forbidden_terms:
            blocked_reasons.append("forbidden_payment_copy")
    elif money_gate.get("gate_status") != "experiment":
        gate_status = "blocked"
        blocked_reasons.append("monetization_not_active")
        blocked_reasons.extend(str(reason) for reason in money_gate.get("blocked_reasons", []) if reason)
    elif not _interest_thresholds_met(config, metrics):
        gate_status = "blocked"
        blocked_reasons.append("insufficient_monetization_interest")
    elif not config.get("sandbox_enabled", True):
        gate_status = "blocked"
        blocked_reasons.append("payment_sandbox_disabled")
    else:
        gate_status = "sandbox"

    blocked_reasons = list(dict.fromkeys(blocked_reasons))
    return {
        "gate_id": "payment_readiness_gate.v0.1",
        "generated_at": _utc_now(),
        "gate_status": gate_status,
        "pause_reason": pause_reason,
        "blocked_reasons": blocked_reasons,
        "monetization_gate_status": money_gate.get("gate_status"),
        "minimum_interest_thresholds": config.get("minimum_interest_thresholds", {}),
        "forbidden_terms_found": forbidden_terms,
        "enabled_capabilities": config.get("enabled_capabilities", []) if gate_status == "sandbox" else [],
        "next_step": "run_payment_sandbox_preparation" if gate_status == "sandbox" else "return_to_monetization_fix",
    }


def build_payment_metrics(
    root: str | Path | None = None,
    orders_path: str | Path | None = None,
    events_path: str | Path | None = None,
    refunds_path: str | Path | None = None,
    monetization_metrics: Mapping[str, Any] | None = None,
) -> dict:
    from .monetization import build_monetization_metrics

    orders = load_sandbox_orders(root, orders_path)
    events = load_payment_events(root, events_path)
    refunds = load_refund_cases(root, refunds_path)
    money_metrics = dict(monetization_metrics or build_monetization_metrics(root))
    status_counts = Counter(str(order.get("order_status", "unknown")) for order in orders)
    event_counts = Counter(str(event.get("event_type", "unknown")) for event in events)
    visitor_counts: defaultdict[str, int] = defaultdict(int)
    for record in orders + events + refunds:
        visitor_id = str(record.get("visitor_id") or "")
        if visitor_id:
            visitor_counts[visitor_id] += 1
    return {
        "metrics_id": "payment_metrics.v0.1",
        "generated_at": _utc_now(),
        "order_count": len(orders),
        "payment_event_count": len(events),
        "refund_case_count": len(refunds),
        "unique_visitor_count": len(visitor_counts),
        "returning_visitor_count": sum(1 for count in visitor_counts.values() if count >= 2),
        "pending_payment_count": int(status_counts.get("pending_payment", 0)),
        "paid_sandbox_count": int(status_counts.get("paid_sandbox", 0)),
        "failed_count": int(status_counts.get("failed", 0)),
        "canceled_count": int(status_counts.get("canceled", 0)),
        "refunded_count": int(status_counts.get("refunded", 0)),
        "blocked_order_count": int(event_counts.get("payment_blocked", 0)),
        "checkout_started_count": int(event_counts.get("checkout_started", 0)),
        "refund_completed_count": int(event_counts.get("refund_completed", 0)),
        "delete_request_count": sum(1 for record in orders + events + refunds if record.get("delete_request")),
        "status_distribution": dict(status_counts),
        "event_distribution": dict(event_counts),
        "monetization_metrics": money_metrics,
    }


def build_phase15_report(
    root: str | Path | None = None,
    orders_path: str | Path | None = None,
    events_path: str | Path | None = None,
    refunds_path: str | Path | None = None,
    monetization_gate: Mapping[str, Any] | None = None,
    monetization_metrics: Mapping[str, Any] | None = None,
    copyright_review: Mapping[str, Any] | None = None,
    forbidden_terms_found: list[str] | None = None,
) -> dict:
    metrics = build_payment_metrics(root, orders_path, events_path, refunds_path, monetization_metrics)
    gate = build_payment_readiness_gate(
        root,
        monetization_gate=monetization_gate,
        monetization_metrics=monetization_metrics or metrics.get("monetization_metrics", {}),
        copyright_review=copyright_review,
        forbidden_terms_found=forbidden_terms_found,
    )
    tiers = load_membership_tiers(root)
    if gate.get("gate_status") == "sandbox":
        decision = "continue_payment_sandbox_preparation"
    elif gate.get("gate_status") == "paused":
        decision = "pause_and_fix_payment_readiness"
    else:
        decision = "do_not_start_payment_sandbox"
    return {
        "report_id": "phase15_payment_readiness_report.v0.1",
        "generated_at": _utc_now(),
        "payment_readiness_gate": gate,
        "membership_tiers": {
            "tiers_id": tiers.get("tiers_id", "membership_tiers.v0.1"),
            "tier_count": len(tiers.get("tiers", [])),
        },
        "payment_metrics": metrics,
        "decision": decision,
        "next_step": "phase16_real_payment_beta" if decision == "continue_payment_sandbox_preparation" else "return_to_phase14_or_safety_fix",
        "blocked_reasons": gate.get("blocked_reasons", []),
    }
