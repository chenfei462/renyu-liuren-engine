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

from liuren_engine.canary_run import (
    build_canary_metrics,
    build_canary_task_status,
    build_phase11_report,
    build_public_release_gate,
    load_canary_run_config,
    record_canary_session,
)
from liuren_engine.growth import record_growth_event
from liuren_engine.webapp import app


BLOCKING_RULES = {"biyong", "shehai", "yaoke", "maoxing", "bazhuan", "bieze", "fuyin", "fanyin"}


def approved_workflow() -> dict:
    return {
        "workflow_id": "expert_review_workflow.v0.1",
        "tasks": [
            {
                "task_id": f"ERW-{rule.upper()}-001",
                "rule_id": rule,
                "case_ids": [f"ER-{rule.upper()}-001"],
                "source_ids": ["RC-060"],
                "current_output": "candidate trace only",
                "expert_opinion": "allow canary as research-only",
                "decision": "research_only",
                "allow_canary": True,
                "status": "reviewed",
            }
            for rule in sorted(BLOCKING_RULES)
        ],
    }


def good_metrics() -> dict:
    return {
        "metrics_id": "canary_metrics.v0.1",
        "session_count": 25,
        "unique_tester_count": 22,
        "returning_tester_count": 8,
        "completion_count": 21,
        "feedback_submit_count": 14,
        "share_report_count": 6,
        "share_report_generated_count": 6,
        "share_report_user_reach_count": 0,
        "share_report_metrics": {"generated_count": 6, "user_reach_count": 0},
        "learning_card_click_count": 18,
        "story_mode_count": 9,
        "mentor_mode_count": 7,
        "member_interest_count": 2,
        "course_interest_count": 2,
        "business_interest_count": 1,
        "safety_block_count": 0,
        "high_risk_leak_count": 0,
        "hallucination_incident_count": 0,
        "copyright_blocked_visible_count": 0,
        "realtime_tool_bypass_count": 0,
        "deterministic_promise_count": 0,
    }


class PhaseElevenCanaryTests(unittest.TestCase):
    def test_canary_run_config_sets_controlled_user_limits(self):
        config = load_canary_run_config(ROOT)

        self.assertEqual(config["run_id"], "canary_run_config.v0.1")
        self.assertEqual(config["tester_limit_min"], 20)
        self.assertEqual(config["tester_limit_max"], 50)
        self.assertIn("professional", config["allowed_modes"])
        self.assertIn("plain", config["allowed_modes"])
        self.assertIn("story", config["allowed_modes"])
        self.assertIn("mentor", config["allowed_modes"])
        self.assertTrue(config["notice"].startswith("受邀 Canary"))

    def test_public_release_gate_blocks_when_expert_gate_is_not_open(self):
        gate = build_public_release_gate(
            root=ROOT,
            ops_status={
                "status": "blocked",
                "blocked_reasons": ["expert_review_pending"],
                "canary_gate": {
                    "canary_allowed": False,
                    "blocked_reasons": ["expert_review_pending"],
                    "blocked_rules": ["biyong"],
                },
            },
            canary_metrics=good_metrics(),
            release_readiness={"release_status": "blocked", "blocked_reasons": ["expert_review_pending"]},
        )

        self.assertEqual(gate["gate_id"], "public_release_gate.v0.1")
        self.assertEqual(gate["gate_status"], "blocked")
        self.assertIn("canary_not_active", gate["blocked_reasons"])
        self.assertIn("expert_review_pending", gate["blocked_reasons"])

    def test_canary_sessions_are_sanitized_and_metrics_merge_growth_events(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session_path = Path(tmpdir) / "sessions.jsonl"
            growth_path = Path(tmpdir) / "growth.jsonl"
            record_canary_session(
                {
                    "tester_id": "T-001",
                    "session_status": "completed",
                    "mode": "story",
                    "category": "Q-001",
                    "feedback_type": "helpful",
                    "safety_action": "allow_cultural_interpretation",
                    "note": "Bearer abc.secret must be redacted",
                    "audio_blob": "must_not_save",
                    "raw_input": "must_not_save",
                },
                session_log_path=session_path,
            )
            record_canary_session(
                {
                    "tester_id": "T-001",
                    "session_status": "completed",
                    "mode": "mentor",
                    "category": "Q-001",
                    "feedback_type": "source_insufficient",
                    "safety_action": "allow_cultural_interpretation",
                },
                session_log_path=session_path,
            )
            record_growth_event({"tester_id": "T-001", "event_type": "share_report_generated", "mode": "plain"}, growth_events_path=growth_path)
            record_growth_event({"tester_id": "T-001", "event_type": "share_report_user_reached", "mode": "plain"}, growth_events_path=growth_path)
            record_growth_event({"tester_id": "T-001", "event_type": "learning_card_click", "mode": "mentor"}, growth_events_path=growth_path)
            record_growth_event({"tester_id": "T-001", "event_type": "member_interest", "mode": "plain"}, growth_events_path=growth_path)

            rendered = session_path.read_text(encoding="utf-8")
            self.assertNotIn("Bearer abc.secret", rendered)
            self.assertNotIn("audio_blob", rendered)
            self.assertNotIn("raw_input", rendered)

            metrics = build_canary_metrics(session_log_path=session_path, growth_events_path=growth_path)
            self.assertEqual(metrics["metrics_id"], "canary_metrics.v0.1")
            self.assertEqual(metrics["session_count"], 2)
            self.assertEqual(metrics["completion_count"], 2)
            self.assertEqual(metrics["returning_tester_count"], 1)
            self.assertEqual(metrics["story_mode_count"], 1)
            self.assertEqual(metrics["mentor_mode_count"], 1)
            self.assertEqual(metrics["share_report_count"], 1)
            self.assertEqual(metrics["share_report_generated_count"], 1)
            self.assertEqual(metrics["share_report_user_reach_count"], 1)
            self.assertEqual(metrics["learning_card_click_count"], 1)
            self.assertEqual(metrics["member_interest_count"], 1)

    def test_canary_task_status_tracks_per_tester_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_EXPERT_WORKFLOW_PATH": str(Path(tmpdir) / "workflow.json"),
                "LIUREN_OPS_EVENTS_PATH": str(Path(tmpdir) / "ops_events.jsonl"),
            },
        ):
            Path(os.environ["LIUREN_EXPERT_WORKFLOW_PATH"]).write_text(json.dumps(approved_workflow(), ensure_ascii=False), encoding="utf-8")
            session_path = Path(tmpdir) / "sessions.jsonl"
            growth_path = Path(tmpdir) / "growth.jsonl"

            record_canary_session(
                {
                    "tester_id": "T-001",
                    "invite_code": "REN-YU-CANARY-001",
                    "session_status": "completed",
                    "mode": "story",
                    "channel": "realtime",
                    "category": "Q-001",
                },
                session_log_path=session_path,
            )
            record_growth_event(
                {
                    "tester_id": "T-001",
                    "invite_code": "REN-YU-CANARY-001",
                    "event_type": "share_report_generated",
                    "mode": "story",
                    "task_id": "C11-T03",
                },
                growth_events_path=growth_path,
            )
            record_growth_event(
                {
                    "tester_id": "T-001",
                    "invite_code": "REN-YU-CANARY-001",
                    "event_type": "feedback_submitted",
                    "mode": "story",
                    "task_id": "C11-T04",
                },
                growth_events_path=growth_path,
            )

            status = build_canary_task_status(
                root=ROOT,
                tester_id="T-001",
                invite_code="REN-YU-CANARY-001",
                session_log_path=session_path,
                growth_events_path=growth_path,
            )

            self.assertEqual(status["identity_status"], "matched")
            self.assertEqual(status["overall_status"], "blocked")
            self.assertEqual(status["tester_progress"]["completed_task_count"], 4)
            self.assertEqual(status["tester_progress"]["next_task_id"], "")
            task_map = {task["task_id"]: task for task in status["tasks"]}
            self.assertEqual(task_map["C11-T01"]["status"], "completed")
            self.assertEqual(task_map["C11-T02"]["status"], "completed")
            self.assertEqual(task_map["C11-T03"]["status"], "completed")
            self.assertEqual(task_map["C11-T04"]["status"], "completed")

    def test_public_release_gate_blocks_safety_and_quality_incidents(self):
        metrics = good_metrics()
        metrics.update(
            {
                "high_risk_leak_count": 1,
                "realtime_tool_bypass_count": 1,
                "hallucination_incident_count": 1,
            }
        )
        gate = build_public_release_gate(
            root=ROOT,
            ops_status={"status": "canary", "blocked_reasons": [], "canary_gate": {"canary_allowed": True, "blocked_reasons": []}},
            canary_metrics=metrics,
            release_readiness={"release_status": "ready", "blocked_reasons": []},
        )

        self.assertEqual(gate["gate_status"], "blocked")
        self.assertIn("high_risk_leak_detected", gate["blocked_reasons"])
        self.assertIn("realtime_tool_bypass_detected", gate["blocked_reasons"])
        self.assertIn("hallucination_incident_detected", gate["blocked_reasons"])

    def test_public_release_gate_allows_phase12_only_after_thresholds(self):
        gate = build_public_release_gate(
            root=ROOT,
            ops_status={"status": "canary", "blocked_reasons": [], "canary_gate": {"canary_allowed": True, "blocked_reasons": []}},
            canary_metrics=good_metrics(),
            release_readiness={"release_status": "ready", "blocked_reasons": []},
        )

        self.assertEqual(gate["gate_status"], "ready_for_phase12")
        self.assertEqual(gate["blocked_reasons"], [])
        self.assertIn("prepare_public_release", gate["next_step"])

    def test_phase11_api_endpoints_and_session_gate(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_EXPERT_WORKFLOW_PATH": str(Path(tmpdir) / "workflow.json"),
                "LIUREN_BETA_FEEDBACK_PATH": str(Path(tmpdir) / "beta_feedback.jsonl"),
                "LIUREN_OPS_EVENTS_PATH": str(Path(tmpdir) / "ops_events.jsonl"),
                "LIUREN_CANARY_SESSION_LOG_PATH": str(Path(tmpdir) / "sessions.jsonl"),
                "LIUREN_GROWTH_EVENTS_PATH": str(Path(tmpdir) / "growth.jsonl"),
            },
        ):
            Path(os.environ["LIUREN_EXPERT_WORKFLOW_PATH"]).write_text(json.dumps(approved_workflow(), ensure_ascii=False), encoding="utf-8")

            config = client.get("/api/canary/run/config")
            self.assertEqual(config.status_code, 200)
            self.assertEqual(config.json()["run_id"], "canary_run_config.v0.1")

            denied = client.post("/api/canary/session", json={"tester_id": "BAD", "mode": "story", "session_status": "completed"})
            self.assertEqual(denied.status_code, 200)
            self.assertFalse(denied.json()["stored"])
            self.assertIn("canary_access_denied", denied.json()["blocked_reasons"])

            stored = client.post("/api/canary/session", json={"tester_id": "T-001", "mode": "story", "session_status": "completed", "feedback_type": "helpful"})
            self.assertEqual(stored.status_code, 200)
            self.assertTrue(stored.json()["stored"])

            metrics = client.get("/api/canary/metrics")
            self.assertEqual(metrics.status_code, 200)
            self.assertEqual(metrics.json()["metrics_id"], "canary_metrics.v0.1")
            self.assertEqual(metrics.json()["session_count"], 1)

            public_gate = client.get("/api/public-release/gate")
            self.assertEqual(public_gate.status_code, 200)
            self.assertEqual(public_gate.json()["gate_id"], "public_release_gate.v0.1")

            task_status = client.get("/api/canary/tasks/status?tester_id=T-001")
            self.assertEqual(task_status.status_code, 200)
            self.assertEqual(task_status.json()["status_id"], "canary_task_status.v0.1")

            report = client.get("/api/phase11/report")
            self.assertEqual(report.status_code, 200)
            self.assertEqual(report.json()["report_id"], "phase11_canary_report.v0.1")

    def test_write_api_state_isolated_before_canary_gate_checks(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_EXPERT_WORKFLOW_PATH": str(Path(tmpdir) / "workflow.json"),
                "LIUREN_BETA_FEEDBACK_PATH": str(Path(tmpdir) / "beta_feedback.jsonl"),
                "LIUREN_OPS_EVENTS_PATH": str(Path(tmpdir) / "ops_events.jsonl"),
                "LIUREN_CANARY_SESSION_LOG_PATH": str(Path(tmpdir) / "sessions.jsonl"),
                "LIUREN_GROWTH_EVENTS_PATH": str(Path(tmpdir) / "growth.jsonl"),
            },
        ):
            Path(os.environ["LIUREN_EXPERT_WORKFLOW_PATH"]).write_text(json.dumps(approved_workflow(), ensure_ascii=False), encoding="utf-8")

            feedback = client.post("/api/beta/feedback", json={"tester_id": "T-001", "feedback_type": "helpful", "category": "Q-001", "mode": "plain"})
            self.assertEqual(feedback.status_code, 200)
            self.assertTrue(feedback.json()["stored"])
            ops_event = client.post("/api/ops/event", json={"event_type": "api_smoke", "severity": "P3", "summary": "isolated test write"})
            self.assertEqual(ops_event.status_code, 200)
            self.assertTrue(ops_event.json()["stored"])

            denied = client.post("/api/canary/session", json={"tester_id": "BAD", "mode": "story", "session_status": "completed"})
            self.assertEqual(denied.status_code, 200)
            self.assertFalse(denied.json()["stored"])
            self.assertIn("canary_access_denied", denied.json()["blocked_reasons"])

            stored = client.post("/api/canary/session", json={"tester_id": "T-001", "mode": "story", "session_status": "completed"})
            self.assertEqual(stored.status_code, 200)
            self.assertTrue(stored.json()["stored"])

    def test_frontend_and_schema_contracts_exist(self):
        release_html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        realtime_html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        realtime_js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="phase11Canary"', release_html)
        self.assertIn("/api/public-release/gate", release_html)
        self.assertIn("/api/canary/metrics", release_html)
        self.assertIn('id="canaryTaskList"', realtime_html)
        self.assertIn('id="commercialInterest"', realtime_html)
        self.assertIn("recordCanarySession", realtime_js)
        self.assertIn('fetch("/api/canary/session"', realtime_js)
        self.assertIn("recordCommercialInterest", realtime_js)
        for schema_name in [
            "canary_run_config.response.schema.json",
            "canary_session.request.schema.json",
            "canary_session.response.schema.json",
            "canary_metrics.response.schema.json",
            "public_release_gate.response.schema.json",
            "phase11_report.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
