import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine.payment import (
    build_payment_metrics,
    build_payment_readiness_gate,
    build_phase15_report,
    cancel_sandbox_order,
    confirm_sandbox_payment,
    create_sandbox_checkout,
    load_membership_tiers,
    load_payment_config,
    refund_sandbox_order,
)
from liuren_engine.webapp import app


def experiment_monetization_gate() -> dict:
    return {
        "gate_id": "monetization_gate.v0.1",
        "gate_status": "experiment",
        "blocked_reasons": [],
        "enabled_experiments": ["offer_interest", "b2b_lead_capture"],
    }


def monetization_interest_metrics() -> dict:
    return {
        "metrics_id": "monetization_metrics.v0.1",
        "event_count": 8,
        "business_lead_count": 2,
        "member_interest_count": 3,
        "course_interest_count": 2,
        "business_interest_count": 2,
        "ip_interest_count": 1,
        "pricing_view_count": 4,
        "offer_click_count": 6,
        "product_metrics": {
            "public_metrics": {
                "critical_incident_count": 0,
                "incident_distribution": {},
            },
        },
    }


class PhaseFifteenPaymentTests(unittest.TestCase):
    def test_payment_config_keeps_sandbox_only(self):
        config = load_payment_config(ROOT)

        self.assertEqual(config["config_id"], "payment_config.v0.1")
        self.assertEqual(config["gate_statuses"], ["blocked", "sandbox", "paused"])
        self.assertEqual(config["provider"], "mock_sandbox")
        self.assertTrue(config["sandbox_enabled"])
        self.assertFalse(config["production_payments_enabled"])
        self.assertFalse(config["real_charge_enabled"])
        self.assertFalse(config["requires_account_system"])

    def test_payment_gate_blocks_until_monetization_experiment(self):
        gate = build_payment_readiness_gate(
            root=ROOT,
            monetization_gate={"gate_status": "blocked", "blocked_reasons": ["productization_not_active"]},
            monetization_metrics=monetization_interest_metrics(),
            copyright_review={"items": []},
            forbidden_terms_found=[],
        )

        self.assertEqual(gate["gate_id"], "payment_readiness_gate.v0.1")
        self.assertEqual(gate["gate_status"], "blocked")
        self.assertIn("monetization_not_active", gate["blocked_reasons"])
        self.assertIn("productization_not_active", gate["blocked_reasons"])

    def test_payment_gate_blocks_until_interest_thresholds_are_met(self):
        metrics = monetization_interest_metrics()
        metrics["member_interest_count"] = 0
        metrics["pricing_view_count"] = 0
        gate = build_payment_readiness_gate(
            root=ROOT,
            monetization_gate=experiment_monetization_gate(),
            monetization_metrics=metrics,
            copyright_review={"items": []},
            forbidden_terms_found=[],
        )

        self.assertEqual(gate["gate_status"], "blocked")
        self.assertIn("insufficient_monetization_interest", gate["blocked_reasons"])

    def test_payment_gate_pauses_on_public_copyright_or_copy_risk(self):
        metrics = monetization_interest_metrics()
        metrics["product_metrics"]["public_metrics"] = {
            "critical_incident_count": 1,
            "incident_distribution": {"deterministic_promise": 1},
        }
        gate = build_payment_readiness_gate(
            root=ROOT,
            monetization_gate=experiment_monetization_gate(),
            monetization_metrics=metrics,
            copyright_review={"items": [{"item_id": "blocked-modern", "status": "blocked", "visible_in_product": True}]},
            forbidden_terms_found=["forbidden-copy"],
        )

        self.assertEqual(gate["gate_status"], "paused")
        self.assertEqual(gate["pause_reason"], "risk_or_compliance_block")
        self.assertIn("critical_public_incident", gate["blocked_reasons"])
        self.assertIn("copyright_blocked_visible", gate["blocked_reasons"])
        self.assertIn("forbidden_payment_copy", gate["blocked_reasons"])

    def test_payment_gate_allows_sandbox_when_monetization_is_clean(self):
        gate = build_payment_readiness_gate(
            root=ROOT,
            monetization_gate=experiment_monetization_gate(),
            monetization_metrics=monetization_interest_metrics(),
            copyright_review={"items": []},
            forbidden_terms_found=[],
        )

        self.assertEqual(gate["gate_status"], "sandbox")
        self.assertEqual(gate["blocked_reasons"], [])
        self.assertIn("mock_sandbox_checkout", gate["enabled_capabilities"])

    def test_membership_tiers_are_sandbox_only_and_safe(self):
        tiers = load_membership_tiers(ROOT)
        categories = {tier["category"] for tier in tiers["tiers"]}

        self.assertEqual(tiers["tiers_id"], "membership_tiers.v0.1")
        self.assertTrue({"free", "membership", "course", "b2b", "ip_presale"}.issubset(categories))
        self.assertTrue(all(tier["sandbox_only"] is True for tier in tiers["tiers"]))
        self.assertTrue(all(tier["high_risk_unlocked"] is False for tier in tiers["tiers"]))
        self.assertTrue(all(tier["unreviewed_complex_rules_unlocked"] is False for tier in tiers["tiers"]))
        rendered = json.dumps(tiers, ensure_ascii=False).lower()
        for forbidden_key in ["payment_url", "checkout_url", "price_id", "stripe", "wechatpay", "alipay"]:
            self.assertNotIn(forbidden_key, rendered)

    def test_sandbox_order_state_machine_and_sanitization(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orders_path = Path(tmpdir) / "orders.jsonl"
            events_path = Path(tmpdir) / "payment_events.jsonl"
            refunds_path = Path(tmpdir) / "refunds.jsonl"

            checkout = create_sandbox_checkout(
                {
                    "visitor_id": "V-001",
                    "tier_id": "tier-membership-v0",
                    "note": "Bearer secret.token must be redacted",
                    "audio_blob": "must_not_save",
                    "raw_input": "must_not_save",
                },
                orders_path=orders_path,
                events_path=events_path,
            )
            self.assertEqual(checkout["order"]["order_status"], "pending_payment")

            paid = confirm_sandbox_payment(
                checkout["order"]["order_id"],
                outcome="success",
                orders_path=orders_path,
                events_path=events_path,
            )
            self.assertEqual(paid["order"]["order_status"], "paid_sandbox")

            refunded = refund_sandbox_order(
                checkout["order"]["order_id"],
                reason="refund requested",
                orders_path=orders_path,
                events_path=events_path,
                refunds_path=refunds_path,
            )
            self.assertEqual(refunded["order"]["order_status"], "refunded")

            second = create_sandbox_checkout(
                {"visitor_id": "V-002", "tier_id": "tier-course-v0"},
                orders_path=orders_path,
                events_path=events_path,
            )
            canceled = cancel_sandbox_order(
                second["order"]["order_id"],
                reason="changed mind",
                orders_path=orders_path,
                events_path=events_path,
            )
            self.assertEqual(canceled["order"]["order_status"], "canceled")

            failed = confirm_sandbox_payment(
                "unknown-order",
                outcome="success",
                orders_path=orders_path,
                events_path=events_path,
            )
            self.assertEqual(failed["order"]["order_status"], "blocked")

            rendered = orders_path.read_text(encoding="utf-8") + events_path.read_text(encoding="utf-8")
            self.assertNotIn("Bearer secret.token", rendered)
            self.assertNotIn("audio_blob", rendered)
            self.assertNotIn("raw_input", rendered)

            metrics = build_payment_metrics(orders_path=orders_path, events_path=events_path, refunds_path=refunds_path)
            self.assertEqual(metrics["metrics_id"], "payment_metrics.v0.1")
            self.assertEqual(metrics["order_count"], 5)
            self.assertEqual(metrics["paid_sandbox_count"], 1)
            self.assertEqual(metrics["refunded_count"], 1)
            self.assertEqual(metrics["canceled_count"], 1)
            self.assertEqual(metrics["blocked_order_count"], 1)

    def test_phase15_api_contract_and_default_gate(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_PAYMENT_ORDERS_PATH": str(Path(tmpdir) / "orders.jsonl"),
                "LIUREN_PAYMENT_EVENTS_PATH": str(Path(tmpdir) / "events.jsonl"),
                "LIUREN_REFUND_CASES_PATH": str(Path(tmpdir) / "refunds.jsonl"),
                "LIUREN_MONETIZATION_EVENTS_PATH": str(Path(tmpdir) / "monetization_events.jsonl"),
                "LIUREN_BUSINESS_LEADS_PATH": str(Path(tmpdir) / "business_leads.jsonl"),
                "LIUREN_VISITOR_PROFILE_PATH": str(Path(tmpdir) / "visitor_profile.jsonl"),
                "LIUREN_LEARNING_PROGRESS_PATH": str(Path(tmpdir) / "learning_progress.jsonl"),
                "LIUREN_PUBLIC_INCIDENTS_PATH": str(Path(tmpdir) / "public_incidents.jsonl"),
                "LIUREN_PUBLIC_SESSION_LOG_PATH": str(Path(tmpdir) / "public_sessions.jsonl"),
                "LIUREN_GROWTH_EVENTS_PATH": str(Path(tmpdir) / "growth.jsonl"),
            },
        ):
            self.assertEqual(client.get("/api/payment/config").json()["config_id"], "payment_config.v0.1")
            self.assertEqual(client.get("/api/payment/gate").json()["gate_status"], "blocked")
            self.assertEqual(client.get("/api/membership/tiers").json()["tiers_id"], "membership_tiers.v0.1")

            checkout = client.post("/api/payment/checkout", json={"visitor_id": "V-001", "tier_id": "tier-membership-v0"})
            self.assertEqual(checkout.status_code, 200)
            self.assertFalse(checkout.json()["stored"])
            self.assertIn("payment_not_active", checkout.json()["blocked_reasons"])

            confirm = client.post("/api/payment/sandbox/confirm", json={"order_id": "order-1", "outcome": "success"})
            self.assertEqual(confirm.status_code, 200)
            self.assertFalse(confirm.json()["stored"])

            cancel = client.post("/api/payment/cancel", json={"order_id": "order-1"})
            self.assertEqual(cancel.status_code, 200)
            self.assertFalse(cancel.json()["stored"])

            refund = client.post("/api/payment/refund", json={"order_id": "order-1"})
            self.assertEqual(refund.status_code, 200)
            self.assertFalse(refund.json()["stored"])

            self.assertEqual(client.get("/api/payment/metrics").json()["metrics_id"], "payment_metrics.v0.1")
            report = client.get("/api/phase15/report")
            self.assertEqual(report.status_code, 200)
            self.assertEqual(report.json()["report_id"], "phase15_payment_readiness_report.v0.1")
            self.assertEqual(report.json()["decision"], "do_not_start_payment_sandbox")

    def test_phase15_report_uses_gate_decision(self):
        report = build_phase15_report(
            root=ROOT,
            monetization_gate=experiment_monetization_gate(),
            monetization_metrics=monetization_interest_metrics(),
            copyright_review={"items": []},
            forbidden_terms_found=[],
        )

        self.assertEqual(report["report_id"], "phase15_payment_readiness_report.v0.1")
        self.assertEqual(report["decision"], "continue_payment_sandbox_preparation")
        self.assertEqual(report["payment_readiness_gate"]["gate_status"], "sandbox")
        self.assertIn("payment_metrics", report)

    def test_frontend_and_schema_contracts_exist(self):
        release_html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        realtime_html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        realtime_js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="phase15Payment"', release_html)
        self.assertIn("/api/payment/gate", release_html)
        self.assertIn("/api/payment/metrics", release_html)
        self.assertIn('id="membershipTiersPanel"', realtime_html)
        self.assertIn('id="sandboxPaymentPanel"', realtime_html)
        self.assertIn("loadPaymentGate", realtime_js)
        self.assertIn('"/api/payment/checkout"', realtime_js)
        self.assertIn('"/api/payment/sandbox/confirm"', realtime_js)
        self.assertIn('"/api/payment/refund"', realtime_js)
        for schema_name in [
            "payment_config.response.schema.json",
            "payment_gate.response.schema.json",
            "membership_tiers.response.schema.json",
            "payment_checkout.request.schema.json",
            "payment_order.response.schema.json",
            "payment_confirm.request.schema.json",
            "payment_cancel.request.schema.json",
            "payment_refund.request.schema.json",
            "payment_metrics.response.schema.json",
            "phase15_report.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
