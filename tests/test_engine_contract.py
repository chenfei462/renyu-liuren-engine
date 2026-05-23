import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine import create_liuren_chart


class EngineContractTests(unittest.TestCase):
    def test_create_chart_returns_required_contract_fields(self):
        chart = create_liuren_chart(
            {
                "question": "合作项目能不能推进？",
                "datetime": "2026-04-30T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "category": "Q-001",
                "manual_params": {
                    "month_general": "子",
                    "divination_hour": "卯",
                    "ganzhi_day": "甲子",
                    "school_version": "school_v0_research_default",
                },
            }
        )

        required = {
            "chart_id",
            "school_version",
            "datetime_normalized",
            "ganzhi",
            "month_general",
            "earth_plate",
            "heaven_plate",
            "four_lessons",
            "three_transmissions",
            "generals",
            "shensha",
            "rule_trace",
            "safety",
        }
        self.assertTrue(required.issubset(chart))
        self.assertEqual(chart["school_version"], "school_v0_research_default")
        self.assertEqual(chart["month_general"], "子")
        self.assertEqual(chart["rule_trace"]["month_general_policy"], "manual_override")
        self.assertEqual(chart["rule_trace"]["divination_hour_policy"], "manual_override")
        self.assertEqual(chart["ganzhi"]["day"], "甲子")
        self.assertEqual(len(chart["earth_plate"]), 12)
        self.assertEqual(len(chart["heaven_plate"]), 12)
        self.assertEqual(len(chart["four_lessons"]), 4)
        self.assertEqual(len(chart["generals"]), 12)
        self.assertIn("selected_transmission_rule", chart["rule_trace"])

    def test_manual_month_general_adds_to_manual_hour_on_heaven_plate(self):
        chart = create_liuren_chart(
            {
                "question": "测试天地盘",
                "datetime": "2026-04-30T10:30:00+08:00",
                "timezone": "Asia/Shanghai",
                "category": "Q-013",
                "manual_params": {
                    "month_general": "午",
                    "divination_hour": "子",
                    "ganzhi_day": "甲子",
                },
            }
        )

        palace_to_heaven = {item["earth_branch"]: item["heaven_branch"] for item in chart["heaven_plate"]}
        self.assertEqual(palace_to_heaven["子"], "午")
        self.assertEqual(palace_to_heaven["丑"], "未")
        self.assertEqual(palace_to_heaven["亥"], "巳")

    def test_yuanshou_and_zhongshen_rules_are_selected_when_unique(self):
        yuanshou = create_liuren_chart(
            {
                "question": "元首样例",
                "datetime": "2026-04-30T10:30:00",
                "timezone": "Asia/Shanghai",
                "category": "Q-013",
                "manual_params": {
                    "month_general": "子",
                    "divination_hour": "卯",
                    "ganzhi_day": "甲子",
                },
            }
        )
        zhongshen = create_liuren_chart(
            {
                "question": "重审样例",
                "datetime": "2026-04-30T10:30:00",
                "timezone": "Asia/Shanghai",
                "category": "Q-013",
                "manual_params": {
                    "month_general": "子",
                    "divination_hour": "辰",
                    "ganzhi_day": "甲子",
                },
            }
        )

        self.assertEqual(yuanshou["rule_trace"]["selected_transmission_rule"], "yuanshou")
        self.assertEqual(yuanshou["three_transmissions"][0]["lesson_type"], "元首")
        self.assertEqual(zhongshen["rule_trace"]["selected_transmission_rule"], "zhongshen")
        self.assertEqual(zhongshen["three_transmissions"][0]["lesson_type"], "重审")

    def test_high_risk_categories_are_safety_only(self):
        for category in ["Q-009", "Q-010", "Q-011", "Q-012"]:
            with self.subTest(category=category):
                chart = create_liuren_chart(
                    {
                        "question": "高风险测试",
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
                self.assertTrue(chart["safety"]["is_high_risk"])
                self.assertEqual(chart["safety"]["action"], "safety_only")
                self.assertTrue(chart["safety"]["disclaimer"])

    def test_schema_files_lock_api_contract_keys(self):
        request_schema = json.loads((ROOT / "schemas" / "create_liuren_chart.request.schema.json").read_text(encoding="utf-8"))
        response_schema = json.loads((ROOT / "schemas" / "create_liuren_chart.response.schema.json").read_text(encoding="utf-8"))

        self.assertEqual(request_schema["required"], ["question", "datetime", "timezone"])
        for key in [
            "chart_id",
            "school_version",
            "datetime_normalized",
            "ganzhi",
            "month_general",
            "earth_plate",
            "heaven_plate",
            "four_lessons",
            "three_transmissions",
            "generals",
            "shensha",
            "safety",
            "rule_trace",
        ]:
            self.assertIn(key, response_schema["required"])

    def test_one_hundred_golden_cases_validate_key_fields(self):
        cases_path = ROOT / "data" / "golden_cases.v0.1.json"
        cases = json.loads(cases_path.read_text(encoding="utf-8"))

        self.assertEqual(len(cases), 100)
        expert_review_count = 0
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                chart = create_liuren_chart(case["input"])
                expected = case["expected"]
                expert_review_count += int(case["needs_expert_review"])
                self.assertEqual(chart["school_version"], "school_v0_research_default")
                self.assertEqual(chart["month_general"], expected["month_general"])
                self.assertEqual(chart["rule_trace"]["selected_transmission_rule"], expected["selected_transmission_rule"])
                self.assertEqual(chart["safety"]["is_high_risk"], expected["is_high_risk"])
                self.assertEqual(len(chart["earth_plate"]), 12)
                self.assertEqual(len(chart["heaven_plate"]), 12)
                self.assertEqual(len(chart["four_lessons"]), 4)
                self.assertEqual(len(chart["generals"]), 12)
                self.assertTrue(chart["rule_trace"]["transmission_candidates"])
                self.assertIn("month_general_policy", chart["rule_trace"])
                self.assertIn("general_policy", chart["rule_trace"])

        self.assertGreaterEqual(expert_review_count, 20)


if __name__ == "__main__":
    unittest.main()
