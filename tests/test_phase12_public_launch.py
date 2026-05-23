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

from liuren_engine.public_launch import (
    build_phase12_report,
    build_public_metrics,
    build_public_status,
    load_public_incidents,
    load_public_launch_config,
    record_public_incident,
    record_public_session,
)
from liuren_engine.growth import record_growth_event
from liuren_engine.webapp import app


def ready_gate() -> dict:
    return {
        "gate_id": "public_release_gate.v0.1",
        "gate_status": "ready_for_phase12",
        "blocked_reasons": [],
        "next_step": "prepare_public_release",
    }


class PhaseTwelvePublicLaunchTests(unittest.TestCase):
    def test_public_config_keeps_mvp_low_risk_and_non_commercial(self):
        config = load_public_launch_config(ROOT)

        self.assertEqual(config["config_id"], "public_launch_config.v0.1")
        self.assertEqual(config["statuses"], ["blocked", "preview", "live", "paused"])
        self.assertFalse(config["payments_enabled"])
        self.assertFalse(config["accounts_enabled"])
        self.assertIn("Q-001", config["allowed_categories"])
        for category in ["Q-009", "Q-010", "Q-011", "Q-012"]:
            self.assertIn(category, config["blocked_categories"])

    def test_public_status_blocks_when_release_gate_is_not_ready(self):
        status = build_public_status(
            root=ROOT,
            public_release_gate={
                "gate_status": "blocked",
                "blocked_reasons": ["expert_review_pending"],
            },
            incidents=[],
        )

        self.assertEqual(status["launch_status"], "blocked")
        self.assertIn("public_release_gate_blocked", status["blocked_reasons"])
        self.assertIn("expert_review_pending", status["blocked_reasons"])

    def test_public_status_allows_preview_when_gate_is_ready(self):
        status = build_public_status(root=ROOT, public_release_gate=ready_gate(), incidents=[])

        self.assertEqual(status["launch_status"], "preview")
        self.assertEqual(status["blocked_reasons"], [])
        self.assertIn("low_risk_public_mvp", status["allowed_scope"])

    def test_p0_or_p1_public_incident_pauses_launch(self):
        status = build_public_status(
            root=ROOT,
            public_release_gate=ready_gate(),
            incidents=[{"event_type": "high_risk_leak", "severity": "P1"}],
        )

        self.assertEqual(status["launch_status"], "paused")
        self.assertEqual(status["pause_reason"], "critical_public_incident")
        self.assertIn("critical_public_incident", status["blocked_reasons"])

    def test_public_session_sanitizes_and_metrics_merge_growth(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session_path = Path(tmpdir) / "public_sessions.jsonl"
            incidents_path = Path(tmpdir) / "public_incidents.jsonl"
            growth_path = Path(tmpdir) / "growth.jsonl"
            record_public_session(
                {
                    "visitor_id": "V-001",
                    "session_status": "completed",
                    "mode": "story",
                    "category": "Q-001",
                    "feedback_type": "helpful",
                    "safety_action": "allow_cultural_interpretation",
                    "event_type": "share_report_generated",
                    "note": "Bearer abc.secret must be redacted",
                    "audio_blob": "must_not_save",
                    "raw_input": "must_not_save",
                },
                session_log_path=session_path,
            )
            record_public_session(
                {
                    "visitor_id": "V-002",
                    "session_status": "blocked",
                    "mode": "plain",
                    "category": "Q-011",
                    "feedback_type": "safety_issue",
                    "safety_action": "safety_only",
                    "blocked_reasons": ["high_risk_category"],
                },
                session_log_path=session_path,
            )
            record_growth_event({"tester_id": "public", "event_type": "share_report_generated", "mode": "plain"}, growth_events_path=growth_path)
            record_growth_event({"tester_id": "public", "event_type": "share_report_user_reached", "mode": "plain"}, growth_events_path=growth_path)
            record_growth_event({"tester_id": "public", "event_type": "member_interest", "mode": "plain"}, growth_events_path=growth_path)

            rendered = session_path.read_text(encoding="utf-8")
            self.assertNotIn("Bearer abc.secret", rendered)
            self.assertNotIn("audio_blob", rendered)
            self.assertNotIn("raw_input", rendered)

            metrics = build_public_metrics(
                root=ROOT,
                session_log_path=session_path,
                growth_events_path=growth_path,
                incidents_path=incidents_path,
            )
            self.assertEqual(metrics["metrics_id"], "public_metrics.v0.1")
            self.assertEqual(metrics["session_count"], 2)
            self.assertEqual(metrics["completion_count"], 1)
            self.assertEqual(metrics["feedback_submit_count"], 2)
            self.assertEqual(metrics["safety_block_count"], 1)
            self.assertEqual(metrics["high_risk_trigger_count"], 1)
            self.assertEqual(metrics["share_report_count"], 2)
            self.assertEqual(metrics["share_report_generated_count"], 2)
            self.assertEqual(metrics["share_report_user_reach_count"], 1)
            self.assertEqual(metrics["member_interest_count"], 1)

    def test_public_incident_recording_pauses_and_redacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            incidents_path = Path(tmpdir) / "public_incidents.jsonl"
            record = record_public_incident(
                {
                    "event_type": "copyright_complaint",
                    "severity": "P1",
                    "summary": "sk-secret must be redacted",
                    "raw_input": "must_not_save",
                },
                incidents_path=incidents_path,
            )
            rendered = incidents_path.read_text(encoding="utf-8")
            self.assertEqual(record["event_type"], "copyright_complaint")
            self.assertNotIn("sk-secret", rendered)
            self.assertNotIn("raw_input", rendered)

            status = build_public_status(
                root=ROOT,
                public_release_gate=ready_gate(),
                incidents=load_public_incidents(incidents_path=incidents_path),
            )
            self.assertEqual(status["launch_status"], "paused")

    def test_phase12_api_and_interpret_pause_guard(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_PUBLIC_SESSION_LOG_PATH": str(Path(tmpdir) / "public_sessions.jsonl"),
                "LIUREN_PUBLIC_INCIDENTS_PATH": str(Path(tmpdir) / "public_incidents.jsonl"),
                "LIUREN_GROWTH_EVENTS_PATH": str(Path(tmpdir) / "growth.jsonl"),
                "LIUREN_OPS_EVENTS_PATH": str(Path(tmpdir) / "ops.jsonl"),
            },
        ):
            config = client.get("/api/public/config")
            self.assertEqual(config.status_code, 200)
            self.assertEqual(config.json()["config_id"], "public_launch_config.v0.1")

            default_status = client.get("/api/public/status")
            self.assertEqual(default_status.status_code, 200)
            self.assertEqual(default_status.json()["launch_status"], "blocked")

            session = client.post("/api/public/session", json={"visitor_id": "V-001", "mode": "plain", "session_status": "completed"})
            self.assertEqual(session.status_code, 200)
            self.assertFalse(session.json()["stored"])
            self.assertIn("public_not_active", session.json()["blocked_reasons"])

            incident = client.post(
                "/api/public/incident",
                json={"event_type": "high_risk_leak", "severity": "P1", "summary": "must pause"},
            )
            self.assertEqual(incident.status_code, 200)
            self.assertTrue(incident.json()["stored"])
            self.assertEqual(incident.json()["status"]["launch_status"], "paused")

            paused = client.post(
                "/api/liuren/interpret",
                json={
                    "question": "问合作能不能推进",
                    "datetime": "2026-04-30T12:00:00+08:00",
                    "timezone": "Asia/Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                },
            )
            self.assertEqual(paused.status_code, 200)
            self.assertIsNone(paused.json()["chart"])
            self.assertIn("public_paused", paused.json()["interpretation"]["blocked_reasons"])

            metrics = client.get("/api/public/metrics")
            self.assertEqual(metrics.status_code, 200)
            self.assertEqual(metrics.json()["metrics_id"], "public_metrics.v0.1")

            report = client.get("/api/phase12/report")
            self.assertEqual(report.status_code, 200)
            self.assertEqual(report.json()["report_id"], "phase12_public_launch_report.v0.1")

    def test_phase12_report_blocks_without_ready_gate(self):
        report = build_phase12_report(
            root=ROOT,
            public_release_gate={"gate_status": "blocked", "blocked_reasons": ["canary_not_active"]},
        )

        self.assertEqual(report["report_id"], "phase12_public_launch_report.v0.1")
        self.assertEqual(report["decision"], "do_not_open_public_mvp")
        self.assertIn("canary_not_active", report["public_status"]["blocked_reasons"])

    def test_frontend_and_schema_contracts_exist(self):
        release_html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        realtime_html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        realtime_js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="phase12Public"', release_html)
        self.assertIn("/api/public/status", release_html)
        self.assertIn("/api/public/metrics", release_html)
        self.assertIn('id="publicFeedbackNotice"', realtime_html)
        self.assertIn("loadPublicStatus", realtime_js)
        self.assertIn('fetch("/api/public/session"', realtime_js)
        for schema_name in [
            "public_config.response.schema.json",
            "public_status.response.schema.json",
            "public_session.request.schema.json",
            "public_session.response.schema.json",
            "public_metrics.response.schema.json",
            "public_incident.request.schema.json",
            "public_incident.response.schema.json",
            "phase12_report.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
