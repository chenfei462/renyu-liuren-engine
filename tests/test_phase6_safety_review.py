import json
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine import create_liuren_chart, generate_interpretation, retrieve_evidence
from liuren_engine.safety_review import (
    load_copyright_review,
    load_expert_review_cases,
    load_red_team_cases,
    load_safety_policy,
    validate_beta_readiness,
    validate_safety,
)
from liuren_engine.webapp import app


def chart_for(category: str = "Q-001", question: str = "合作项目能不能推进？") -> dict:
    return create_liuren_chart(
        {
            "question": question,
            "datetime": "2026-04-30T10:30:00",
            "timezone": "Asia/Shanghai",
            "category": category,
            "manual_params": {
                "month_general": "子",
                "divination_hour": "卯",
                "ganzhi_day": "甲子",
            },
        }
    )


class PhaseSixSafetyReviewTests(unittest.TestCase):
    def test_safety_policy_covers_required_risk_areas(self):
        policy = load_safety_policy(ROOT)

        self.assertEqual(policy["policy_id"], "safety_policy.v0.1")
        required = {"medical", "legal", "investment", "personal_safety", "privacy", "manipulation", "deterministic_prediction", "timing_promise", "single_shensha_conclusion"}
        self.assertTrue(required.issubset({item["risk_id"] for item in policy["risk_areas"]}))
        self.assertIn("包赢", policy["forbidden_terms"])
        self.assertIn("必赚", policy["forbidden_terms"])

    def test_interpretation_contains_safety_validation_and_beta_flags(self):
        chart = chart_for()
        evidence = retrieve_evidence(chart, mode="mentor")
        answer = generate_interpretation(chart, evidence, mode="mentor")

        self.assertIn("safety_validation", answer)
        self.assertIn("beta_readiness_flags", answer)
        self.assertIn("blocked_reasons", answer)
        self.assertTrue(answer["safety_validation"]["passed"])
        self.assertEqual(answer["blocked_reasons"], [])
        self.assertIn("low_risk_mode_allowed", answer["beta_readiness_flags"])

    def test_high_risk_story_and_share_report_are_safety_validated(self):
        chart = chart_for(category="Q-011", question="我该不该买这只股票？")
        evidence = retrieve_evidence(chart, mode="story")
        answer = generate_interpretation(chart, evidence, mode="story")
        report = answer["entertainment"]["share_report"]

        self.assertEqual(chart["safety"]["action"], "safety_only")
        self.assertEqual(answer["plain_explanation"], [])
        self.assertEqual(answer["entertainment"]["persona_lines"], [])
        self.assertTrue(answer["safety_validation"]["passed"])
        self.assertIn("high_risk_safety_only", answer["beta_readiness_flags"])
        self.assertIn("传统文化学习与娱乐体验", report["text"])

    def test_unsafe_question_is_not_echoed_in_visible_answer_fields(self):
        chart = chart_for(category="Q-010", question="预测这个官司我是不是能胜诉。")
        evidence = retrieve_evidence(chart, mode="mentor")
        answer = generate_interpretation(chart, evidence, mode="mentor")

        rendered_answer = json.dumps(
            {
                "overview": answer.get("overview"),
                "plain_explanation": answer.get("plain_explanation"),
                "action_prompts": answer.get("action_prompts"),
                "entertainment": answer.get("entertainment"),
            },
            ensure_ascii=False,
        )
        self.assertNotIn("胜诉", rendered_answer)
        self.assertEqual(answer["question_focus"]["question"], "预测这个官司我是不是能胜诉。")
        self.assertEqual(answer["question_focus"]["display_question"], "当前问题")

    def test_high_risk_category_normalizes_chinese_labels_and_question_keywords(self):
        cases = [
            {"category": "投资", "question": "我该不该买这只股票？", "raw_category": "投资"},
            {"category": None, "question": "我该不该买这只股票？", "raw_category": None},
            {"category": "Q-011", "question": "我该不该买这只股票？", "raw_category": None},
        ]
        for case in cases:
            with self.subTest(category=case["category"]):
                chart = create_liuren_chart(
                    {
                        "question": case["question"],
                        "datetime": "2026-04-30T10:30:00",
                        "timezone": "Asia/Shanghai",
                        "category": case["category"],
                    }
                )
                evidence = retrieve_evidence(chart, mode="plain")
                answer = generate_interpretation(chart, evidence, mode="plain")

                self.assertEqual(chart["category"], "Q-011")
                self.assertEqual(chart["safety"]["action"], "safety_only")
                self.assertTrue(chart["safety"]["is_high_risk"])
                self.assertEqual(answer["plain_explanation"], [])
                if case["raw_category"]:
                    self.assertEqual(chart["rule_trace"]["raw_category"], case["raw_category"])

        low_risk = chart_for(category="Q-001", question="合作项目能不能推进？")
        self.assertEqual(low_risk["category"], "Q-001")
        self.assertEqual(low_risk["safety"]["action"], "allow_cultural_interpretation")

    def test_validate_safety_blocks_forbidden_terms_and_single_shensha_claims(self):
        chart = chart_for()
        unsafe = {
            "overview": "此事包赢",
            "rule_reasoning": [{"judgment": "神煞辅助", "note": "只看神煞即可下结论"}],
            "plain_explanation": [],
            "action_prompts": [],
        }
        report = validate_safety(unsafe, chart, mode="professional")

        self.assertFalse(report["passed"])
        self.assertIn("forbidden_terms", report["blocked_reasons"])
        self.assertIn("single_shensha_conclusion", report["blocked_reasons"])

    def test_red_team_cases_trigger_expected_safety_actions(self):
        cases = load_red_team_cases(ROOT)
        self.assertGreaterEqual(len(cases), 8)
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                chart = chart_for(category=case["category"], question=case["question"])
                evidence = retrieve_evidence(chart, mode=case["mode"])
                answer = generate_interpretation(chart, evidence, mode=case["mode"])
                report = validate_safety(answer, chart, mode=case["mode"])

                self.assertEqual(report["action"], case["expected_action"])
                self.assertEqual(report["passed"], case["expected_passed"])

    def test_expert_and_copyright_review_support_beta_readiness(self):
        expert_cases = load_expert_review_cases(ROOT)
        copyright_review = load_copyright_review(ROOT)
        readiness = validate_beta_readiness(
            {
                "expert_cases": expert_cases,
                "copyright_review": copyright_review,
                "red_team_passed": True,
                "golden_cases_passed": True,
            }
        )

        self.assertGreaterEqual(len(expert_cases["cases"]), 100)
        self.assertIn("biyong", {case.get("rule_id") for case in expert_cases["cases"]})
        self.assertIn("blocked", {item["beta_status"] for item in copyright_review["items"]})
        self.assertFalse(readiness["ready_for_beta"])
        self.assertIn("expert_review_pending", readiness["blocked_reasons"])
        self.assertIn("copyright_blocked_items", readiness["blocked_reasons"])
        self.assertIn("学习", readiness["allowed_beta_scope"])

    def test_phase_six_api_endpoints(self):
        client = TestClient(app)

        policy_response = client.get("/api/safety/policy")
        self.assertEqual(policy_response.status_code, 200)
        self.assertEqual(policy_response.json()["policy_id"], "safety_policy.v0.1")

        chart = chart_for()
        evidence = retrieve_evidence(chart, mode="plain")
        answer = generate_interpretation(chart, evidence, mode="plain")
        validation_response = client.post(
            "/api/safety/validate",
            json={"answer": answer, "chart": chart, "mode": "plain"},
        )
        self.assertEqual(validation_response.status_code, 200)
        self.assertTrue(validation_response.json()["passed"])

        status_response = client.get("/api/review/status")
        self.assertEqual(status_response.status_code, 200)
        status = status_response.json()
        self.assertGreaterEqual(status["expert_review"]["case_count"], 100)
        self.assertIn("ready_for_beta", status["beta_readiness"])
        self.assertNotIn("red_team_not_passed", status["beta_readiness"]["blocked_reasons"])
        self.assertNotIn("golden_cases_not_passed", status["beta_readiness"]["blocked_reasons"])

    def test_phase_six_schema_files_exist(self):
        for schema_name in [
            "safety_validate.request.schema.json",
            "safety_validate.response.schema.json",
            "safety_policy.response.schema.json",
            "review_status.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
