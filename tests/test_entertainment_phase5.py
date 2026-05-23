import json
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine import create_liuren_chart, generate_interpretation, retrieve_evidence
from liuren_engine.constants import GENERAL_NAMES
from liuren_engine.entertainment import build_share_report, load_general_personas, load_learning_cards
from liuren_engine.webapp import app


def sample_chart(category: str = "Q-001") -> dict:
    return create_liuren_chart(
        {
            "question": "合作项目能不能推进？",
            "datetime": "2026-04-30T10:30:00",
            "timezone": "Asia/Shanghai",
            "location": "Shanghai",
            "category": category,
            "manual_params": {
                "month_general": "子",
                "divination_hour": "卯",
                "ganzhi_day": "甲子",
            },
        }
    )


class EntertainmentPhaseFiveTests(unittest.TestCase):
    def test_persona_and_learning_data_cover_phase_five_contract(self):
        personas = load_general_personas(ROOT)
        learning_cards = load_learning_cards(ROOT)

        self.assertEqual({item["general"] for item in personas}, set(GENERAL_NAMES))
        for persona in personas:
            for key in [
                "general",
                "role_name",
                "tone",
                "symbols",
                "usable_expression",
                "safety_boundaries",
                "source_ids",
            ]:
                self.assertIn(key, persona)
            self.assertTrue(persona["source_ids"])

        self.assertGreaterEqual(len(learning_cards), 8)
        for card in learning_cards:
            self.assertIn("card_id", card)
            self.assertIn("title", card)
            self.assertIn("summary", card)
            self.assertIn("tags", card)
            self.assertIn("source_ids", card)

    def test_story_mode_adds_persona_lines_without_replacing_evidence(self):
        chart = sample_chart()
        evidence = retrieve_evidence(chart, mode="story")
        answer = generate_interpretation(chart, evidence, mode="story")
        rendered = json.dumps(answer, ensure_ascii=False)

        self.assertEqual(answer["mode"], "story")
        self.assertIn("entertainment", answer)
        self.assertIn("文化娱乐", answer["entertainment"]["story_scene"])
        self.assertGreaterEqual(len(answer["entertainment"]["persona_lines"]), 1)
        self.assertTrue(answer["evidence"])
        self.assertIn("元首", answer["overview"])
        for forbidden in ["必然", "一定", "保证", "准确率"]:
            self.assertNotIn(forbidden, rendered)

    def test_mentor_mode_explains_rule_path_and_learning_cards(self):
        chart = sample_chart()
        evidence = retrieve_evidence(chart, mode="mentor")
        answer = generate_interpretation(chart, evidence, mode="mentor")
        mentor_steps = answer["entertainment"]["mentor_steps"]

        self.assertEqual(answer["mode"], "mentor")
        self.assertGreaterEqual(len(mentor_steps), 1)
        self.assertTrue(any(step.get("rule_id") == "yuanshou" for step in mentor_steps))
        self.assertTrue(any("RC-045" in step.get("source_ids", []) for step in mentor_steps))
        self.assertGreaterEqual(len(answer["entertainment"]["learning_cards"]), 3)
        self.assertLessEqual(len(answer["entertainment"]["learning_cards"]), 5)

    def test_high_risk_story_mode_is_safety_only(self):
        chart = sample_chart(category="Q-011")
        evidence = retrieve_evidence(chart, mode="story")
        answer = generate_interpretation(chart, evidence, mode="story")

        self.assertEqual(answer["safety_notice"]["action"], "safety_only")
        self.assertEqual(answer["plain_explanation"], [])
        self.assertEqual(answer["entertainment"]["persona_lines"], [])
        self.assertEqual(answer["entertainment"]["story_scene"], "")
        self.assertEqual(answer["entertainment"]["mentor_steps"], [])

    def test_share_report_is_local_copyable_payload(self):
        chart = sample_chart()
        evidence = retrieve_evidence(chart, mode="story")
        answer = generate_interpretation(chart, evidence, mode="story")
        report = build_share_report(chart, answer)

        self.assertEqual(report["report_type"], "local_share_report")
        self.assertEqual(report["chart_id"], chart["chart_id"])
        self.assertIn("html", report)
        self.assertIn("text", report)
        self.assertIn("content", report)
        self.assertIn("sections", report)
        self.assertIn("artifacts", report)
        self.assertIn("share_channels", report)
        self.assertIn("tracking", report)
        self.assertIn("传统文化学习与娱乐体验", report["text"])
        self.assertIn(chart["chart_id"], report["html"])
        self.assertEqual(report["tracking"]["legacy_count_semantics"], "generated_count")
        self.assertEqual(report["tracking"]["user_reach_event_type"], "share_report_user_reached")
        self.assertEqual(report["artifacts"]["pdf_report_draft"]["format"], "pdf_draft")
        self.assertEqual(report["content"]["chart_facts"]["chart_id"], chart["chart_id"])

    def test_phase_five_api_endpoints(self):
        client = TestClient(app)

        personas = client.get("/api/personas")
        self.assertEqual(personas.status_code, 200)
        self.assertEqual(len(personas.json()["personas"]), 12)

        cards = client.get("/api/learning/cards")
        self.assertEqual(cards.status_code, 200)
        self.assertGreaterEqual(len(cards.json()["learning_cards"]), 8)

        tool_response = client.post(
            "/api/liuren/interpret",
            json={
                "question": "合作项目能不能推进？",
                "datetime": "2026-04-30T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "category": "Q-001",
                "mode": "story",
            },
        )
        self.assertEqual(tool_response.status_code, 200)
        payload = tool_response.json()
        self.assertEqual(payload["interpretation"]["mode"], "story")
        self.assertIn("share_report", payload["interpretation"]["entertainment"])

        report_response = client.post(
            "/api/report/share",
            json={"chart": payload["chart"], "interpretation": payload["interpretation"]},
        )
        self.assertEqual(report_response.status_code, 200)
        self.assertIn("local_share_report", report_response.json()["report_type"])


if __name__ == "__main__":
    unittest.main()
