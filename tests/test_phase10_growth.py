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

from liuren_engine.growth import (
    build_growth_metrics,
    build_growth_report,
    build_review_gate,
    load_canary_config,
    load_content_calendar,
    load_expert_review_workflow,
    record_growth_event,
    validate_canary_access,
)
from liuren_engine.ops import build_ops_status
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
                "current_output": "候选轨迹保留",
                "expert_opinion": "canary 可展示为研究性标签",
                "decision": "research_only",
                "allow_canary": True,
                "status": "reviewed",
            }
            for rule in sorted(BLOCKING_RULES)
        ],
    }


class PhaseTenGrowthTests(unittest.TestCase):
    def test_expert_review_workflow_covers_blocking_rules(self):
        workflow = load_expert_review_workflow(ROOT)
        rules = {task["rule_id"] for task in workflow["tasks"]}

        self.assertEqual(workflow["workflow_id"], "expert_review_workflow.v0.1")
        self.assertTrue(BLOCKING_RULES.issubset(rules))
        self.assertTrue({task["decision"] for task in workflow["tasks"]}.issubset({"approved_for_canary", "blocked_until_reworked", "research_only"}))
        self.assertGreaterEqual(sum(1 for task in workflow["tasks"] if task["decision"] == "blocked_until_reworked"), 1)

    def test_review_gate_blocks_until_all_critical_tasks_are_processed(self):
        gate = build_review_gate(
            expert_workflow={
                "workflow_id": "expert_review_workflow.v0.1",
                "tasks": [
                    {"rule_id": "biyong", "decision": "blocked_until_reworked", "allow_canary": False},
                    {"rule_id": "shehai", "decision": "research_only", "allow_canary": True},
                ],
            }
        )

        self.assertFalse(gate["canary_allowed"])
        self.assertIn("biyong", gate["blocked_rules"])
        self.assertIn("expert_review_pending", gate["blocked_reasons"])

    def test_review_gate_unlocks_ops_canary_when_release_block_is_only_expert_review(self):
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(os.environ, {"LIUREN_EXPERT_WORKFLOW_PATH": str(Path(tmpdir) / "workflow.json")}):
            Path(os.environ["LIUREN_EXPERT_WORKFLOW_PATH"]).write_text(json.dumps(approved_workflow(), ensure_ascii=False), encoding="utf-8")

            status = build_ops_status(
                root=ROOT,
                release_readiness={
                    "release_status": "blocked",
                    "blocked_reasons": ["expert_review_pending"],
                    "needs_expert_review": {"rules": sorted(BLOCKING_RULES)},
                },
                events=[],
            )

            self.assertEqual(status["status"], "canary")
            self.assertTrue(status["canary_gate"]["canary_allowed"])
            self.assertEqual(status["blocked_reasons"], [])

    def test_canary_validation_accepts_known_tester_or_invite_only(self):
        config = load_canary_config(ROOT)
        valid_by_tester = validate_canary_access({"tester_id": "T-001"}, config)
        valid_by_invite = validate_canary_access({"invite_code": "REN-YU-CANARY-001"}, config)
        invalid = validate_canary_access({"tester_id": "BAD", "invite_code": "BAD"}, config)

        self.assertEqual(config["canary_id"], "canary_testers.v0.1")
        self.assertTrue(valid_by_tester["allowed"])
        self.assertTrue(valid_by_invite["allowed"])
        self.assertFalse(invalid["allowed"])
        self.assertIn("invalid_canary_credentials", invalid["blocked_reasons"])

    def test_growth_events_are_sanitized_and_metrics_count_interest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            events_path = Path(tmpdir) / "growth_events.jsonl"
            record_growth_event(
                {
                    "tester_id": "T-001",
                    "event_type": "member_interest",
                    "mode": "story",
                    "note": "sk-secret should be removed",
                    "audio_blob": "must_not_save",
                },
                growth_events_path=events_path,
            )
            record_growth_event({"tester_id": "T-001", "event_type": "share_report_generated", "mode": "plain"}, growth_events_path=events_path)
            record_growth_event({"tester_id": "T-001", "event_type": "share_report_user_reached", "mode": "plain"}, growth_events_path=events_path)
            metrics = build_growth_metrics(growth_events_path=events_path)

            rendered = events_path.read_text(encoding="utf-8")
            self.assertNotIn("sk-secret", rendered)
            self.assertNotIn("audio_blob", rendered)
            self.assertEqual(metrics["metrics_id"], "growth_metrics.v0.1")
            self.assertEqual(metrics["member_interest_count"], 1)
            self.assertEqual(metrics["share_report_count"], 1)
            self.assertEqual(metrics["share_report_generated_count"], 1)
            self.assertEqual(metrics["share_report_user_reach_count"], 1)
            self.assertEqual(metrics["share_report_metrics"]["legacy_count_semantics"], "generated_count")
            self.assertEqual(metrics["returning_tester_count"], 1)

    def test_content_calendar_uses_safe_operational_columns(self):
        calendar = load_content_calendar(ROOT)

        self.assertEqual(calendar["calendar_id"], "content_calendar.v0.1")
        self.assertGreaterEqual(len(calendar["items"]), 5)
        topics = {item["column"] for item in calendar["items"]}
        self.assertIn("一分钟懂三传", topics)
        self.assertIn("天将电台", topics)
        self.assertIn("古籍拆读", topics)
        rendered = json.dumps(calendar, ensure_ascii=False)
        for forbidden in ["准确率保证", "包赢", "必赚", "确诊", "用药", "胜诉"]:
            self.assertNotIn(forbidden, rendered)

    def test_phase_ten_api_and_interpret_canary_gate(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "LIUREN_EXPERT_WORKFLOW_PATH": str(Path(tmpdir) / "workflow.json"),
                "LIUREN_BETA_FEEDBACK_PATH": str(Path(tmpdir) / "beta_feedback.jsonl"),
                "LIUREN_OPS_EVENTS_PATH": str(Path(tmpdir) / "ops_events.jsonl"),
                "LIUREN_GROWTH_EVENTS_PATH": str(Path(tmpdir) / "growth.jsonl"),
            },
        ):
            Path(os.environ["LIUREN_EXPERT_WORKFLOW_PATH"]).write_text(json.dumps(approved_workflow(), ensure_ascii=False), encoding="utf-8")

            tasks = client.get("/api/expert/review/tasks")
            self.assertEqual(tasks.status_code, 200)
            self.assertEqual(tasks.json()["workflow_id"], "expert_review_workflow.v0.1")

            canary = client.post("/api/canary/validate", json={"tester_id": "T-001"})
            self.assertEqual(canary.status_code, 200)
            self.assertTrue(canary.json()["allowed"])

            denied = client.post(
                "/api/liuren/interpret",
                json={
                    "question": "合作项目能不能推进？",
                    "datetime": "2026-04-30T10:30:00",
                    "timezone": "Asia/Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                    "tester_id": "BAD",
                },
            )
            self.assertEqual(denied.status_code, 200)
            self.assertIsNone(denied.json()["chart"])
            self.assertIn("canary_access_denied", denied.json()["interpretation"]["blocked_reasons"])

            allowed = client.post(
                "/api/liuren/interpret",
                json={
                    "question": "合作项目能不能推进？",
                    "datetime": "2026-04-30T10:30:00",
                    "timezone": "Asia/Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                    "tester_id": "T-001",
                },
            )
            self.assertEqual(allowed.status_code, 200)
            self.assertIsNotNone(allowed.json()["chart"])

            event = client.post("/api/growth/event", json={"tester_id": "T-001", "event_type": "course_interest", "note": "Bearer abc.secret"})
            self.assertEqual(event.status_code, 200)
            self.assertNotIn("Bearer abc.secret", json.dumps(event.json(), ensure_ascii=False))

            report = build_growth_report(root=ROOT, growth_events_path=Path(os.environ["LIUREN_GROWTH_EVENTS_PATH"]))
            self.assertEqual(report["report_id"], "phase10_growth_report.v0.1")

    def test_frontend_and_schema_contracts_exist(self):
        release_html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        realtime_html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        realtime_js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="canaryStatus"', release_html)
        self.assertIn("/api/content/calendar", release_html)
        self.assertIn('id="inviteCode"', realtime_html)
        self.assertIn("validateCanaryAccess", realtime_js)
        self.assertIn('fetch("/api/canary/validate"', realtime_js)
        for schema_name in [
            "expert_review_workflow.response.schema.json",
            "canary_validate.request.schema.json",
            "canary_validate.response.schema.json",
            "content_calendar.response.schema.json",
            "growth_metrics.response.schema.json",
            "growth_event.request.schema.json",
            "growth_report.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
