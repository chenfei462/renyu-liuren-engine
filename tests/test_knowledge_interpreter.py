import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine import create_liuren_chart, generate_interpretation, retrieve_evidence
from liuren_engine.knowledge import build_source_cards_from_phase1


def yuanshou_chart():
    return create_liuren_chart(
        {
            "question": "合作项目能不能推进？",
            "datetime": "2026-04-30T10:30:00",
            "timezone": "Asia/Shanghai",
            "category": "Q-001",
            "manual_params": {
                "month_general": "子",
                "divination_hour": "卯",
                "ganzhi_day": "甲子",
                "school_version": "school_v0_research_default",
            },
        }
    )


class KnowledgeInterpreterTests(unittest.TestCase):
    def test_build_source_cards_from_phase1_markdown(self):
        cards = build_source_cards_from_phase1(ROOT)
        by_id = {card["source_id"]: card for card in cards}

        self.assertGreaterEqual(len(cards), 100)
        self.assertIn("RC-045", by_id)
        self.assertEqual(by_id["RC-045"]["claim_type"], "现代转述")
        self.assertIn("元首", by_id["RC-045"]["summary"])
        for key in [
            "source_id",
            "book_or_source",
            "chapter_or_location",
            "claim_type",
            "summary",
            "tags",
            "safety_note",
            "copyright_status",
        ]:
            self.assertIn(key, by_id["RC-045"])

    def test_retrieve_evidence_uses_exact_source_cards_and_keywords(self):
        chart = yuanshou_chart()
        cards = retrieve_evidence(chart, query="青龙 合作", mode="professional")
        source_ids = {card["source_id"] for card in cards}

        self.assertIn("RC-045", source_ids)
        self.assertIn("RC-053", source_ids)
        self.assertIn("RC-055", source_ids)
        self.assertTrue({"RC-068", "RC-070"} & source_ids)

    def test_professional_interpretation_has_sections_and_coverage(self):
        chart = yuanshou_chart()
        evidence = retrieve_evidence(chart, mode="professional")
        answer = generate_interpretation(chart, evidence, mode="professional")

        for key in [
            "overview",
            "chart_facts",
            "evidence",
            "rule_reasoning",
            "plain_explanation",
            "action_prompts",
            "safety_notice",
            "evidence_coverage",
        ]:
            self.assertIn(key, answer)
        self.assertGreaterEqual(answer["evidence_coverage"]["ratio"], 0.8)
        self.assertIn("元首", answer["overview"])
        self.assertTrue(any(item["source_id"] == "RC-045" for item in answer["evidence"]))

    def test_professional_interpretation_refuses_without_chart_or_evidence(self):
        with self.assertRaises(ValueError):
            generate_interpretation(None, [], mode="professional")

        chart = yuanshou_chart()
        answer = generate_interpretation(chart, [], mode="professional")
        self.assertEqual(answer["overview"], "依据不足")
        self.assertEqual(answer["evidence_coverage"]["ratio"], 0)
        self.assertEqual(answer["evidence"], [])

    def test_plain_mode_avoids_deterministic_predictions(self):
        chart = yuanshou_chart()
        evidence = retrieve_evidence(chart, mode="plain")
        answer = generate_interpretation(chart, evidence, mode="plain")
        rendered = json.dumps(answer, ensure_ascii=False)

        for forbidden in ["必然", "一定", "保证", "准确率"]:
            self.assertNotIn(forbidden, rendered)
        self.assertGreaterEqual(answer["evidence_coverage"]["ratio"], 0.8)

    def test_high_risk_interpretation_is_safety_only(self):
        chart = create_liuren_chart(
            {
                "question": "我该不该买这只股票？",
                "datetime": "2026-04-30T10:30:00",
                "timezone": "Asia/Shanghai",
                "category": "Q-011",
                "manual_params": {
                    "month_general": "子",
                    "divination_hour": "卯",
                    "ganzhi_day": "甲子",
                },
            }
        )
        evidence = retrieve_evidence(chart, mode="professional")
        answer = generate_interpretation(chart, evidence, mode="professional")

        self.assertTrue(answer["safety_notice"]["is_high_risk"])
        self.assertEqual(answer["safety_notice"]["action"], "safety_only")
        self.assertEqual(answer["plain_explanation"], [])
        self.assertTrue(answer["action_prompts"])

    def test_all_golden_cases_have_professional_coverage(self):
        cases = json.loads((ROOT / "data" / "golden_cases.v0.1.json").read_text(encoding="utf-8"))
        ratios = []
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                chart = create_liuren_chart(case["input"])
                evidence = retrieve_evidence(chart, mode="professional")
                answer = generate_interpretation(chart, evidence, mode="professional")
                ratio = answer["evidence_coverage"]["ratio"]
                ratios.append(ratio)
                self.assertGreaterEqual(ratio, 0.8)
        self.assertEqual(len(ratios), 100)

    def test_schema_files_and_cli_interpret_command(self):
        for schema_name in [
            "retrieve_evidence.request.schema.json",
            "generate_interpretation.request.schema.json",
            "source_cards.response.schema.json",
            "structured_answer.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")

        for schema_name in [
            "generate_interpretation.request.schema.json",
            "liuren_interpret_tool.request.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["properties"]["mode"]["enum"], ["professional", "plain", "story", "mentor"])

        request = {
            "question": "合作项目能不能推进？",
            "datetime": "2026-04-30T10:30:00",
            "timezone": "Asia/Shanghai",
            "category": "Q-001",
            "manual_params": {
                "month_general": "子",
                "divination_hour": "卯",
                "ganzhi_day": "甲子",
            },
            "mode": "professional",
        }
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(request, handle, ensure_ascii=False)
            request_path = handle.name

        result = subprocess.run(
            [sys.executable, "-m", "liuren_engine.interpret_cli", "--request", request_path],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertIn("chart", payload)
        self.assertIn("interpretation", payload)
        self.assertGreaterEqual(payload["interpretation"]["evidence_coverage"]["ratio"], 0.8)


if __name__ == "__main__":
    unittest.main()
