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

from liuren_engine.beta import record_beta_feedback
from liuren_engine.ops import (
    build_feedback_triage,
    build_ops_metrics,
    build_ops_report,
    build_ops_status,
    load_ops_config,
    record_ops_event,
)
from liuren_engine.webapp import app


class PhaseNineOpsTests(unittest.TestCase):
    def test_ops_status_respects_blocked_release_gate(self):
        status = build_ops_status(
            root=ROOT,
            release_readiness={
                "release_status": "blocked",
                "blocked_reasons": ["expert_review_pending"],
                "needs_expert_review": {"rules": ["biyong"]},
            },
            events=[],
        )

        self.assertEqual(status["status"], "blocked")
        self.assertIn("expert_review_pending", status["blocked_reasons"])
        self.assertIn("biyong", status["review_queue"]["rules"])
        self.assertNotEqual(status["status"], "canary")

    def test_p0_or_p1_ops_event_pauses_the_system(self):
        status = build_ops_status(
            root=ROOT,
            release_readiness={"release_status": "ready", "blocked_reasons": [], "needs_expert_review": {"rules": []}},
            events=[
                {
                    "event_id": "EVT-001",
                    "event_type": "high_risk_leak",
                    "severity": "P1",
                    "summary": "高风险建议漏拦截",
                }
            ],
        )

        self.assertEqual(status["status"], "paused")
        self.assertEqual(status["pause_reason"], "critical_ops_event")
        self.assertEqual(status["critical_event_count"], 1)

    def test_feedback_triage_marks_review_required_items(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            feedback_path = Path(tmpdir) / "feedback.jsonl"
            record_beta_feedback(
                {
                    "tester_id": "U01",
                    "chart_id": "chart_safe",
                    "mode": "plain",
                    "category": "Q-001",
                    "safety_action": "allow_cultural_interpretation",
                    "blocked_reasons": [],
                    "feedback_type": "helpful",
                    "note": "ok",
                },
                feedback_path=feedback_path,
            )
            record_beta_feedback(
                {
                    "tester_id": "U02",
                    "chart_id": "chart_review",
                    "mode": "story",
                    "category": "Q-011",
                    "safety_action": "safety_only",
                    "blocked_reasons": ["blocked_from_beta_interpretation"],
                    "feedback_type": "safety_issue",
                    "note": "需要复核",
                },
                feedback_path=feedback_path,
            )
            triage = build_feedback_triage(root=ROOT, feedback_path=feedback_path)

            self.assertEqual(triage["triage_id"], "feedback_triage.v0.1")
            self.assertEqual(triage["summary"]["total_feedback"], 2)
            self.assertEqual(triage["summary"]["needs_expert_review"], 1)
            review_item = next(item for item in triage["items"] if item["chart_id"] == "chart_review")
            self.assertEqual(review_item["triage_status"], "needs_expert_review")
            self.assertIn("high_risk_category", review_item["review_reasons"])

    def test_ops_metrics_count_events_feedback_and_reports(self):
        metrics = build_ops_metrics(
            root=ROOT,
            beta_report={
                "session_count": 4,
                "completion_count": 2,
                "feedback_count": 3,
                "safety_block_count": 1,
                "failed_interface_count": 1,
                "mode_distribution": {"plain": 2, "story": 1, "mentor": 1},
                "feedback_distribution": {"helpful": 1, "voice_issue": 1, "safety_issue": 1},
            },
            events=[
                {"event_type": "api_failure", "severity": "P2"},
                {"event_type": "realtime_failure", "severity": "P2"},
                {"event_type": "share_report_generated", "severity": "P3"},
                {"event_type": "share_report_user_reached", "severity": "P3"},
            ],
        )

        self.assertEqual(metrics["metrics_id"], "ops_metrics.v0.1")
        self.assertEqual(metrics["session_count"], 4)
        self.assertEqual(metrics["completion_rate"], 0.5)
        self.assertEqual(metrics["api_failure_count"], 1)
        self.assertEqual(metrics["realtime_failure_count"], 1)
        self.assertEqual(metrics["share_report_count"], 1)
        self.assertEqual(metrics["share_report_generated_count"], 1)
        self.assertEqual(metrics["share_report_user_reach_count"], 1)
        self.assertEqual(metrics["safety_block_count"], 1)

    def test_ops_api_endpoints_and_pause_guard_interpretation(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_OPS_EVENTS_PATH": str(Path(tmpdir) / "ops_events.jsonl"),
                "LIUREN_BETA_FEEDBACK_PATH": str(Path(tmpdir) / "feedback.jsonl"),
            },
        ):
            config = client.get("/api/ops/status")
            self.assertEqual(config.status_code, 200)
            self.assertIn(config.json()["status"], {"blocked", "canary", "paused"})

            event_response = client.post(
                "/api/ops/event",
                json={"event_type": "realtime_failure", "severity": "P2", "summary": "SDP failed", "OPENAI_API_KEY": "sk-secret"},
            )
            self.assertEqual(event_response.status_code, 200)
            rendered = json.dumps(event_response.json(), ensure_ascii=False)
            self.assertNotIn("sk-secret", rendered)

            pause = client.post("/api/ops/pause", json={"reason": "manual red-team drill"})
            self.assertEqual(pause.status_code, 200)
            self.assertEqual(pause.json()["status"]["status"], "paused")

            interpret = client.post(
                "/api/liuren/interpret",
                json={
                    "question": "合作项目能不能推进？",
                    "datetime": "2026-04-30T10:30:00",
                    "timezone": "Asia/Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                },
            )
            self.assertEqual(interpret.status_code, 200)
            body = interpret.json()
            self.assertIsNone(body["chart"])
            self.assertEqual(body["interpretation"]["ops_status"]["status"], "paused")
            self.assertIn("暂停", body["interpretation"]["overview"])

            resume = client.post("/api/ops/resume", json={"reason": "drill complete"})
            self.assertEqual(resume.status_code, 200)
            self.assertIn(resume.json()["status"]["status"], {"blocked", "canary"})

            metrics = client.get("/api/ops/metrics")
            self.assertEqual(metrics.status_code, 200)
            self.assertEqual(metrics.json()["metrics_id"], "ops_metrics.v0.1")

            triage = client.get("/api/ops/feedback/triage")
            self.assertEqual(triage.status_code, 200)
            self.assertEqual(triage.json()["triage_id"], "feedback_triage.v0.1")

    def test_ops_report_and_schema_files_exist(self):
        config = load_ops_config(ROOT)
        report = build_ops_report(root=ROOT, status={"status": "blocked"}, metrics={"metrics_id": "ops_metrics.v0.1"}, triage={"triage_id": "feedback_triage.v0.1"})

        self.assertEqual(config["ops_id"], "ops_config.v0.1")
        self.assertEqual(report["report_id"], "phase9_ops_report.v0.1")
        for schema_name in [
            "ops_status.response.schema.json",
            "ops_metrics.response.schema.json",
            "ops_event.request.schema.json",
            "feedback_triage.response.schema.json",
            "ops_report.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")

    def test_frontend_surfaces_ops_status_and_pause_notice(self):
        release_html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        realtime_html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        realtime_js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="opsStatus"', release_html)
        self.assertIn("/api/ops/status", release_html)
        self.assertIn('id="opsPauseNotice"', realtime_html)
        self.assertIn("loadOpsStatus", realtime_js)
        self.assertIn('fetch("/api/ops/status"', realtime_js)
        self.assertIn("ops_paused", realtime_js)


if __name__ == "__main__":
    unittest.main()
