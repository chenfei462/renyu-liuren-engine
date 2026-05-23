from __future__ import annotations

import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _configure_vercel_runtime_storage() -> None:
    if not os.getenv("VERCEL"):
        return
    runtime_root = Path(os.getenv("LIUREN_RUNTIME_DIR", "/tmp/liuren"))
    defaults = {
        "LIUREN_BETA_FEEDBACK_PATH": "beta_feedback.jsonl",
        "LIUREN_OPS_EVENTS_PATH": "ops_events.jsonl",
        "LIUREN_CANARY_SESSION_LOG_PATH": "canary_session_log.jsonl",
        "LIUREN_GROWTH_EVENTS_PATH": "growth_events.jsonl",
        "LIUREN_PUBLIC_SESSION_LOG_PATH": "public_session_log.jsonl",
        "LIUREN_PUBLIC_INCIDENTS_PATH": "public_incidents.jsonl",
        "LIUREN_VISITOR_PROFILE_PATH": "visitor_profile.jsonl",
        "LIUREN_LEARNING_PROGRESS_PATH": "learning_progress.jsonl",
        "LIUREN_MONETIZATION_EVENTS_PATH": "monetization_events.jsonl",
        "LIUREN_BUSINESS_LEADS_PATH": "business_leads.jsonl",
        "LIUREN_PAYMENT_ORDERS_PATH": "sandbox_orders.jsonl",
        "LIUREN_PAYMENT_EVENTS_PATH": "payment_events.jsonl",
        "LIUREN_REFUND_CASES_PATH": "refund_cases.jsonl",
    }
    for key, relative_path in defaults.items():
        os.environ.setdefault(key, str(runtime_root / relative_path))


_configure_vercel_runtime_storage()

from liuren_engine.webapp import app  # noqa: E402
