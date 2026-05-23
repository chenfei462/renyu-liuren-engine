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

from liuren_engine.monetization import (
    build_monetization_gate,
    build_monetization_metrics,
    build_phase14_report,
    load_monetization_config,
    load_offer_catalog,
    record_business_lead,
    record_monetization_event,
)
from liuren_engine.webapp import app


def experiment_productization_gate() -> dict:
    return {
        "gate_id": "productization_gate.v0.1",
        "gate_status": "experiment",
        "blocked_reasons": [],
        "enabled_experiments": ["learning_path", "pdf_report_draft"],
    }


def clean_product_metrics() -> dict:
    return {
        "metrics_id": "product_metrics.v0.1",
        "visitor_count": 12,
        "learning_progress_count": 18,
        "pdf_report_draft_count": 6,
        "public_metrics": {
            "critical_incident_count": 0,
            "incident_distribution": {},
        },
    }


class PhaseFourteenMonetizationTests(unittest.TestCase):
    def test_monetization_config_keeps_interest_only_experiment(self):
        config = load_monetization_config(ROOT)

        self.assertEqual(config["config_id"], "monetization_config.v0.1")
        self.assertEqual(config["gate_statuses"], ["blocked", "experiment", "paused"])
        self.assertFalse(config["payments_enabled"])
        self.assertFalse(config["membership_entitlements_enabled"])
        self.assertIn("member_interest", config["allowed_event_types"])
        self.assertIn("business_interest", config["allowed_event_types"])

    def test_monetization_gate_blocks_until_productization_experiment(self):
        gate = build_monetization_gate(
            root=ROOT,
            productization_gate={"gate_status": "blocked", "blocked_reasons": ["public_mvp_not_active"]},
            product_metrics=clean_product_metrics(),
        )

        self.assertEqual(gate["gate_id"], "monetization_gate.v0.1")
        self.assertEqual(gate["gate_status"], "blocked")
        self.assertIn("productization_not_active", gate["blocked_reasons"])
        self.assertIn("public_mvp_not_active", gate["blocked_reasons"])

    def test_monetization_gate_pauses_on_public_or_copyright_risk(self):
        metrics = clean_product_metrics()
        metrics["public_metrics"] = {
            "critical_incident_count": 1,
            "incident_distribution": {"realtime_tool_bypass": 1},
        }
        gate = build_monetization_gate(
            root=ROOT,
            productization_gate=experiment_productization_gate(),
            product_metrics=metrics,
            copyright_review={"items": [{"item_id": "modern-course", "beta_status": "blocked", "visible_in_product": True}]},
        )

        self.assertEqual(gate["gate_status"], "paused")
        self.assertEqual(gate["pause_reason"], "risk_or_copyright_block")
        self.assertIn("critical_public_incident", gate["blocked_reasons"])
        self.assertIn("copyright_blocked_visible", gate["blocked_reasons"])

    def test_monetization_gate_allows_experiment_when_productization_is_clean(self):
        gate = build_monetization_gate(
            root=ROOT,
            productization_gate=experiment_productization_gate(),
            product_metrics=clean_product_metrics(),
            copyright_review={"items": []},
        )

        self.assertEqual(gate["gate_status"], "experiment")
        self.assertEqual(gate["blocked_reasons"], [])
        self.assertIn("offer_interest", gate["enabled_experiments"])

    def test_offer_catalog_covers_all_streams_and_has_no_payment_links(self):
        catalog = load_offer_catalog(ROOT)
        categories = {offer["category"] for offer in catalog["offers"]}

        self.assertEqual(catalog["catalog_id"], "offer_catalog.v0.1")
        self.assertTrue({"free", "membership", "expert_course", "b2b", "ip_goods"}.issubset(categories))
        self.assertTrue(all(offer["interest_only"] is True for offer in catalog["offers"]))
        rendered = json.dumps(catalog, ensure_ascii=False).lower()
        for forbidden_key in ["payment_url", "checkout_url", "price_id", "stripe", "wechatpay", "alipay"]:
            self.assertNotIn(forbidden_key, rendered)

    def test_monetization_events_and_business_leads_are_sanitized_and_counted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            events_path = Path(tmpdir) / "monetization_events.jsonl"
            leads_path = Path(tmpdir) / "business_leads.jsonl"
            record_monetization_event(
                {
                    "visitor_id": "V-001",
                    "event_type": "member_interest",
                    "offer_id": "offer-membership-v0",
                    "note": "Bearer abc.secret must be redacted",
                    "audio_blob": "must_not_save",
                    "raw_input": "must_not_save",
                },
                events_path=events_path,
            )
            record_monetization_event(
                {
                    "visitor_id": "V-001",
                    "event_type": "ip_interest",
                    "offer_id": "offer-ip-v0",
                },
                events_path=events_path,
            )
            record_business_lead(
                {
                    "visitor_id": "V-002",
                    "contact_nickname": "bookstore",
                    "channel": "offline_event",
                    "need_summary": "sk-secret must be redacted",
                    "transcript": "must_not_save",
                    "openai_api_key": "must_not_save",
                },
                leads_path=leads_path,
            )

            rendered = events_path.read_text(encoding="utf-8") + leads_path.read_text(encoding="utf-8")
            self.assertNotIn("Bearer abc.secret", rendered)
            self.assertNotIn("sk-secret", rendered)
            self.assertNotIn("audio_blob", rendered)
            self.assertNotIn("raw_input", rendered)
            self.assertNotIn("transcript", rendered)
            self.assertNotIn("openai_api_key", rendered)

            metrics = build_monetization_metrics(events_path=events_path, leads_path=leads_path)
            self.assertEqual(metrics["metrics_id"], "monetization_metrics.v0.1")
            self.assertEqual(metrics["event_count"], 2)
            self.assertEqual(metrics["member_interest_count"], 1)
            self.assertEqual(metrics["ip_interest_count"], 1)
            self.assertEqual(metrics["business_lead_count"], 1)
            self.assertEqual(metrics["returning_visitor_count"], 1)

    def test_phase14_api_contract_and_default_gate(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_MONETIZATION_EVENTS_PATH": str(Path(tmpdir) / "monetization_events.jsonl"),
                "LIUREN_BUSINESS_LEADS_PATH": str(Path(tmpdir) / "business_leads.jsonl"),
                "LIUREN_VISITOR_PROFILE_PATH": str(Path(tmpdir) / "visitor_profile.jsonl"),
                "LIUREN_LEARNING_PROGRESS_PATH": str(Path(tmpdir) / "learning_progress.jsonl"),
                "LIUREN_PUBLIC_INCIDENTS_PATH": str(Path(tmpdir) / "public_incidents.jsonl"),
                "LIUREN_PUBLIC_SESSION_LOG_PATH": str(Path(tmpdir) / "public_sessions.jsonl"),
                "LIUREN_GROWTH_EVENTS_PATH": str(Path(tmpdir) / "growth.jsonl"),
            },
        ):
            config = client.get("/api/monetization/config")
            self.assertEqual(config.status_code, 200)
            self.assertEqual(config.json()["config_id"], "monetization_config.v0.1")

            gate = client.get("/api/monetization/gate")
            self.assertEqual(gate.status_code, 200)
            self.assertEqual(gate.json()["gate_status"], "blocked")

            offers = client.get("/api/monetization/offers")
            self.assertEqual(offers.status_code, 200)
            self.assertEqual(offers.json()["catalog_id"], "offer_catalog.v0.1")

            event = client.post("/api/monetization/event", json={"visitor_id": "V-001", "event_type": "member_interest"})
            self.assertEqual(event.status_code, 200)
            self.assertFalse(event.json()["stored"])
            self.assertIn("monetization_not_active", event.json()["blocked_reasons"])

            lead = client.post("/api/business/lead", json={"visitor_id": "V-001", "contact_nickname": "venue", "channel": "web"})
            self.assertEqual(lead.status_code, 200)
            self.assertFalse(lead.json()["stored"])
            self.assertIn("monetization_not_active", lead.json()["blocked_reasons"])

            metrics = client.get("/api/monetization/metrics")
            self.assertEqual(metrics.status_code, 200)
            self.assertEqual(metrics.json()["metrics_id"], "monetization_metrics.v0.1")

            report = client.get("/api/phase14/report")
            self.assertEqual(report.status_code, 200)
            self.assertEqual(report.json()["report_id"], "phase14_monetization_report.v0.1")
            self.assertEqual(report.json()["decision"], "do_not_start_monetization")

    def test_phase14_report_uses_gate_decision(self):
        report = build_phase14_report(
            root=ROOT,
            productization_gate=experiment_productization_gate(),
            product_metrics=clean_product_metrics(),
            copyright_review={"items": []},
        )

        self.assertEqual(report["report_id"], "phase14_monetization_report.v0.1")
        self.assertEqual(report["decision"], "continue_monetization_experiment")
        self.assertEqual(report["monetization_gate"]["gate_status"], "experiment")
        self.assertIn("interest_summary", report)

    def test_frontend_and_schema_contracts_exist(self):
        release_html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        realtime_html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        realtime_js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="phase14Monetization"', release_html)
        self.assertIn("/api/monetization/gate", release_html)
        self.assertIn("/api/monetization/metrics", release_html)
        self.assertIn('id="monetizationPanel"', realtime_html)
        self.assertIn('id="businessLeadPanel"', realtime_html)
        self.assertIn('id="commercialInterestSummary"', realtime_html)
        self.assertIn('id="monetizationGateBadge"', realtime_html)
        self.assertIn("loadMonetizationGate", realtime_js)
        self.assertIn("loadMonetizationMetrics", realtime_js)
        self.assertIn('fetch("/api/growth/metrics")', realtime_js)
        self.assertIn('fetch("/api/monetization/event"', realtime_js)
        self.assertIn('fetch("/api/business/lead"', realtime_js)
        for schema_name in [
            "monetization_config.response.schema.json",
            "monetization_gate.response.schema.json",
            "offer_catalog.response.schema.json",
            "monetization_event.request.schema.json",
            "monetization_event.response.schema.json",
            "business_lead.request.schema.json",
            "business_lead.response.schema.json",
            "monetization_metrics.response.schema.json",
            "phase14_report.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
