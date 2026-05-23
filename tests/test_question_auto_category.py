import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine.safety import category_symbols, normalize_category


class QuestionAutoCategoryTests(unittest.TestCase):
    def test_low_risk_questions_map_to_expected_categories(self):
        cases = [
            ("这个合作项目能不能推进？", "Q-001", ["六合", "朱雀"]),
            ("这段关系是否适合继续？", "Q-002", ["天后", "六合"]),
            ("这次面试沟通是否顺利？", "Q-004", ["朱雀", "青龙"]),
            ("这个工作机会适合接吗？", "Q-005", ["贵人", "青龙"]),
        ]

        for question, expected_category, expected_symbols_prefix in cases:
            with self.subTest(question=question):
                self.assertEqual(normalize_category(None, question), expected_category)
                self.assertEqual(
                    category_symbols(None, question)[: len(expected_symbols_prefix)],
                    expected_symbols_prefix,
                )

    def test_high_risk_keywords_still_take_priority(self):
        self.assertEqual(normalize_category(None, "这个投资机会适合现在买吗？"), "Q-011")
        self.assertEqual(normalize_category(None, "这次出行遇到人身安全威胁怎么办？"), "Q-012")

    def test_explicit_low_risk_category_is_preserved(self):
        self.assertEqual(normalize_category("Q-001", "这个合作项目能不能推进？"), "Q-001")
        self.assertEqual(normalize_category("Q-005", "这个工作机会适合接吗？"), "Q-005")

    def test_unmatched_question_stays_unclassified(self):
        self.assertIsNone(normalize_category(None, "最近心情一般，随便聊聊。"))
        self.assertEqual(category_symbols(None, "最近心情一般，随便聊聊。"), [])


if __name__ == "__main__":
    unittest.main()
