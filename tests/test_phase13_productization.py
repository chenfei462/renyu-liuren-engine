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

from liuren_engine.engine import create_liuren_chart
from liuren_engine.interpreter import generate_interpretation
from liuren_engine.knowledge import retrieve_evidence
from liuren_engine.productization import (
    build_phase13_report,
    build_product_metrics,
    build_productization_gate,
    load_learning_path,
    load_productization_config,
    record_learning_progress,
    record_visitor_profile,
)
from liuren_engine.webapp import app


def ready_public_status() -> dict:
    return {
        "status_id": "public_status.v0.1",
        "launch_status": "preview",
        "public_launch_status": "preview",
        "blocked_reasons": [],
        "critical_incident_count": 0,
    }


def ready_public_metrics() -> dict:
    return {
        "metrics_id": "public_metrics.v0.1",
        "session_count": 24,
        "completion_count": 20,
        "feedback_submit_count": 8,
        "critical_incident_count": 0,
        "incident_distribution": {},
        "share_report_count": 4,
        "share_report_generated_count": 4,
        "share_report_user_reach_count": 0,
        "share_report_metrics": {"generated_count": 4, "user_reach_count": 0},
        "learning_card_click_count": 9,
        "member_interest_count": 1,
        "course_interest_count": 1,
        "business_interest_count": 0,
    }


class PhaseThirteenProductizationTests(unittest.TestCase):
    def test_productization_config_keeps_experiments_low_risk_and_non_commercial(self):
        config = load_productization_config(ROOT)

        self.assertEqual(config["config_id"], "productization_config.v0.1")
        self.assertEqual(config["gate_statuses"], ["blocked", "experiment", "paused"])
        self.assertFalse(config["accounts_enabled"])
        self.assertFalse(config["payments_enabled"])
        self.assertIn("learning_path", config["enabled_experiments"])
        self.assertIn("pdf_report_draft", config["enabled_experiments"])

    def test_productization_gate_blocks_until_public_preview_or_live(self):
        gate = build_productization_gate(
            root=ROOT,
            public_status={"launch_status": "blocked", "blocked_reasons": ["public_release_gate_blocked"]},
            public_metrics=ready_public_metrics(),
        )

        self.assertEqual(gate["gate_id"], "productization_gate.v0.1")
        self.assertEqual(gate["gate_status"], "blocked")
        self.assertIn("public_mvp_not_active", gate["blocked_reasons"])
        self.assertIn("public_release_gate_blocked", gate["blocked_reasons"])

    def test_productization_gate_pauses_on_public_p0_or_p1_risk(self):
        gate = build_productization_gate(
            root=ROOT,
            public_status={"launch_status": "paused", "blocked_reasons": ["critical_public_incident"], "critical_incident_count": 1},
            public_metrics={**ready_public_metrics(), "critical_incident_count": 1, "incident_distribution": {"high_risk_leak": 1}},
        )

        self.assertEqual(gate["gate_status"], "paused")
        self.assertEqual(gate["pause_reason"], "public_risk_event")
        self.assertIn("critical_public_incident", gate["blocked_reasons"])

    def test_productization_gate_allows_experiment_when_public_mvp_is_ready(self):
        gate = build_productization_gate(
            root=ROOT,
            public_status=ready_public_status(),
            public_metrics=ready_public_metrics(),
        )

        self.assertEqual(gate["gate_status"], "experiment")
        self.assertEqual(gate["blocked_reasons"], [])
        self.assertIn("learning_path", gate["enabled_experiments"])

    def test_learning_path_covers_core_topics_and_keeps_unreviewed_rules_research_only(self):
        path = load_learning_path(ROOT)
        topics = {node["topic"] for node in path["nodes"]}
        expected = {"four_lessons", "three_transmissions", "nine_rules", "generals", "shensha", "classical_symbols", "safety_boundary"}

        self.assertEqual(path["path_id"], "learning_path.v0.1")
        self.assertTrue(expected.issubset(topics))
        research_nodes = [node for node in path["nodes"] if node["review_status"] == "research_only"]
        self.assertTrue(research_nodes)
        self.assertTrue(all("normal_interpretation" not in node.get("unlocked_outputs", []) for node in research_nodes))

    def test_visitor_and_learning_records_are_sanitized_and_counted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            visitor_path = Path(tmpdir) / "visitor_profile.jsonl"
            progress_path = Path(tmpdir) / "learning_progress.jsonl"
            record_visitor_profile(
                {
                    "visitor_id": "V-001",
                    "nickname": "本地访客",
                    "mode_preference": "mentor",
                    "note": "Bearer abc.secret must be redacted",
                    "audio_blob": "must_not_save",
                    "raw_input": "must_not_save",
                },
                profile_path=visitor_path,
            )
            record_learning_progress(
                {
                    "visitor_id": "V-001",
                    "node_id": "LP-FOUR-001",
                    "event_type": "node_completed",
                    "status": "completed",
                    "reflection_note": "sk-secret must be redacted",
                    "transcript": "must_not_save",
                },
                progress_path=progress_path,
            )
            record_learning_progress(
                {
                    "visitor_id": "V-001",
                    "node_id": "LP-REPORT-001",
                    "event_type": "pdf_report_generated",
                    "status": "completed",
                },
                progress_path=progress_path,
            )

            rendered = visitor_path.read_text(encoding="utf-8") + progress_path.read_text(encoding="utf-8")
            self.assertNotIn("Bearer abc.secret", rendered)
            self.assertNotIn("sk-secret", rendered)
            self.assertNotIn("audio_blob", rendered)
            self.assertNotIn("raw_input", rendered)
            self.assertNotIn("transcript", rendered)

            metrics = build_product_metrics(profile_path=visitor_path, progress_path=progress_path)
            self.assertEqual(metrics["metrics_id"], "product_metrics.v0.1")
            self.assertEqual(metrics["visitor_count"], 1)
            self.assertEqual(metrics["learning_progress_count"], 2)
            self.assertEqual(metrics["completed_node_count"], 2)
            self.assertEqual(metrics["pdf_report_draft_count"], 1)
            self.assertEqual(metrics["returning_visitor_count"], 1)

    def test_share_report_includes_pdf_report_draft(self):
        chart = create_liuren_chart(
            {
                "question": "问合作能不能推进",
                "datetime": "2026-04-30T12:00:00+08:00",
                "timezone": "Asia/Shanghai",
                "category": "Q-001",
            }
        )
        evidence = retrieve_evidence(chart, query="问合作能不能推进", mode="mentor")
        interpretation = generate_interpretation(chart, evidence, mode="mentor")
        client = TestClient(app)

        response = client.post("/api/report/share", json={"chart": chart, "interpretation": interpretation})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["pdf_report_draft"]["format"], "pdf_draft")
        self.assertEqual(payload["pdf_report_draft"]["storage"], "local_only")
        self.assertIn("traditional culture learning", payload["pdf_report_draft"]["disclaimer"])
        self.assertEqual(payload["tracking"]["legacy_count_semantics"], "generated_count")
        self.assertEqual(payload["tracking"]["user_reach_event_type"], "share_report_user_reached")
        self.assertEqual(payload["content"]["chart_facts"]["chart_id"], chart["chart_id"])

    def test_phase13_api_contract_and_productization_gate(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_VISITOR_PROFILE_PATH": str(Path(tmpdir) / "visitor_profile.jsonl"),
                "LIUREN_LEARNING_PROGRESS_PATH": str(Path(tmpdir) / "learning_progress.jsonl"),
                "LIUREN_PUBLIC_INCIDENTS_PATH": str(Path(tmpdir) / "public_incidents.jsonl"),
                "LIUREN_PUBLIC_SESSION_LOG_PATH": str(Path(tmpdir) / "public_sessions.jsonl"),
                "LIUREN_GROWTH_EVENTS_PATH": str(Path(tmpdir) / "growth.jsonl"),
            },
        ):
            config = client.get("/api/productization/config")
            self.assertEqual(config.status_code, 200)
            self.assertEqual(config.json()["config_id"], "productization_config.v0.1")

            gate = client.get("/api/productization/gate")
            self.assertEqual(gate.status_code, 200)
            self.assertEqual(gate.json()["gate_status"], "blocked")

            visitor = client.post("/api/visitor/profile", json={"visitor_id": "V-001", "nickname": "local"})
            self.assertEqual(visitor.status_code, 200)
            self.assertFalse(visitor.json()["stored"])
            self.assertIn("productization_not_active", visitor.json()["blocked_reasons"])

            path = client.get("/api/learning/path")
            self.assertEqual(path.status_code, 200)
            self.assertEqual(path.json()["path_id"], "learning_path.v0.1")

            progress = client.post("/api/learning/progress", json={"visitor_id": "V-001", "node_id": "LP-FOUR-001", "status": "completed"})
            self.assertEqual(progress.status_code, 200)
            self.assertFalse(progress.json()["stored"])
            self.assertIn("productization_not_active", progress.json()["blocked_reasons"])

            metrics = client.get("/api/product/metrics")
            self.assertEqual(metrics.status_code, 200)
            self.assertEqual(metrics.json()["metrics_id"], "product_metrics.v0.1")

            report = client.get("/api/phase13/report")
            self.assertEqual(report.status_code, 200)
            self.assertEqual(report.json()["report_id"], "phase13_productization_report.v0.1")
            self.assertEqual(report.json()["decision"], "do_not_start_productization")

    def test_phase13_report_uses_gate_decision(self):
        report = build_phase13_report(
            root=ROOT,
            public_status=ready_public_status(),
            public_metrics=ready_public_metrics(),
        )

        self.assertEqual(report["report_id"], "phase13_productization_report.v0.1")
        self.assertEqual(report["decision"], "continue_productization_experiment")
        self.assertEqual(report["productization_gate"]["gate_status"], "experiment")

    def test_frontend_and_schema_contracts_exist(self):
        release_html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        realtime_html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        realtime_js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="phase13Productization"', release_html)
        self.assertIn("/api/productization/gate", release_html)
        self.assertIn("/api/product/metrics", release_html)
        self.assertIn('id="visitorProfilePanel"', realtime_html)
        self.assertIn('id="learningPathPanel"', realtime_html)
        self.assertIn("pdf_report_draft", realtime_js)
        self.assertIn("loadProductizationGate", realtime_js)
        self.assertIn('fetch("/api/learning/progress"', realtime_js)
        self.assertIn('fetch("/api/visitor/profile"', realtime_js)
        for schema_name in [
            "productization_config.response.schema.json",
            "productization_gate.response.schema.json",
            "visitor_profile.request.schema.json",
            "visitor_profile.response.schema.json",
            "learning_path.response.schema.json",
            "learning_progress.request.schema.json",
            "learning_progress.response.schema.json",
            "product_metrics.response.schema.json",
            "phase13_report.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
