# Question Auto Category Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic low-risk question auto-classification so uncategorized text requests can map to `Q-001` / `Q-002` / `Q-004` / `Q-005`, populate `category_symbols`, and produce different persona card sets without changing the API surface.

**Architecture:** Keep `normalize_category(...)` as the single classification entrypoint in `safety.py`. Extend it with a small low-risk keyword table that only runs after the existing high-risk checks, then verify the behavior at two layers: a direct normalization unit suite and a realtime service integration suite that posts uncategorized questions through `/api/liuren/text-interpret`. No frontend or schema changes are required because the existing engine and entertainment pipeline already consume `chart.category` and `rule_trace.category_symbols`.

**Tech Stack:** Python, FastAPI, vanilla application modules in `src/liuren_engine`, Python `unittest` executed through `pytest`

---

## File Structure

- Create: `D:\Desktop\六壬\tests\test_question_auto_category.py`
  Add a focused unit suite for `normalize_category(...)` and `category_symbols(...)` so low-risk rule coverage stays local and easy to reason about.
- Modify: `D:\Desktop\六壬\src\liuren_engine\safety.py`
  Add the low-risk keyword table plus a small helper used by `normalize_category(...)`, while preserving existing high-risk behavior.
- Modify: `D:\Desktop\六壬\tests\test_realtime_service.py`
  Add endpoint-level regression coverage proving uncategorized questions now produce non-empty `category_symbols` and different persona card combinations.

### Task 1: Add Direct Rule Tests For Question Auto Classification

**Files:**
- Create: `D:\Desktop\六壬\tests\test_question_auto_category.py`
- Test: `D:\Desktop\六壬\tests\test_question_auto_category.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest D:\Desktop\六壬\tests\test_question_auto_category.py -q`

Expected: `FAIL` because `normalize_category(None, "...")` still returns `None` for the four low-risk questions and `category_symbols(...)` stays empty.

- [ ] **Step 3: Record that Git commit is unavailable in this workspace**

Run: `git -C D:\Desktop\六壬 status --short`

Expected: `fatal: not a git repository (or any of the parent directories): .git`

### Task 2: Implement Low-Risk Keyword Classification In `safety.py`

**Files:**
- Modify: `D:\Desktop\六壬\src\liuren_engine\safety.py`
- Test: `D:\Desktop\六壬\tests\test_question_auto_category.py`

- [ ] **Step 1: Write the minimal implementation**

```python
from .constants import CATEGORY_CLASSIC_SYMBOLS, HIGH_RISK_CATEGORIES


DISCLAIMER = "本产品为传统文化学习与娱乐体验，不构成医疗、法律、投资、职业、婚姻或安全决策建议。"

HIGH_RISK_CATEGORY_KEYWORDS = {
    "Q-009": ("医疗", "健康", "疾病", "确诊", "用药"),
    "Q-010": ("法律", "诉讼", "合同纠纷", "律师"),
    "Q-011": ("投资", "股票", "基金", "理财", "买股", "币"),
    "Q-012": ("人身安全", "自伤", "自杀", "威胁", "危险"),
}

LOW_RISK_CATEGORY_KEYWORDS = {
    "Q-001": ("合作", "推进", "对接", "谈成", "谋望"),
    "Q-002": ("感情", "关系", "复合", "相处", "联系"),
    "Q-004": ("沟通", "消息", "文书", "学习", "考试", "面试", "出行"),
    "Q-005": ("工作", "求职", "职场", "offer", "入职", "岗位", "机会", "发展"),
}


def _matched_category(text: str, keyword_map: dict[str, tuple[str, ...]]) -> str | None:
    for code, keywords in keyword_map.items():
        if any(keyword in text for keyword in keywords):
            return code
    return None


def normalize_category(category: str | None, question: str | None = None) -> str | None:
    raw_category = category.strip() if isinstance(category, str) else ""
    question_text = str(question or "").strip()
    combined = f"{raw_category} {question_text}".strip().casefold()

    if raw_category in HIGH_RISK_CATEGORIES:
        return raw_category

    high_risk = _matched_category(combined, HIGH_RISK_CATEGORY_KEYWORDS)
    if high_risk:
        return high_risk

    if raw_category:
        return raw_category

    low_risk = _matched_category(question_text.casefold(), LOW_RISK_CATEGORY_KEYWORDS)
    if low_risk:
        return low_risk

    return None
```

- [ ] **Step 2: Run the direct rule tests to verify they now pass**

Run: `python -m pytest D:\Desktop\六壬\tests\test_question_auto_category.py -q`

Expected: `PASS` with all low-risk mapping assertions green.

- [ ] **Step 3: Run the existing safety regression suite**

Run: `python -m pytest D:\Desktop\六壬\tests\test_phase6_safety_review.py -q`

Expected: `PASS`, proving the new low-risk rules did not weaken the existing high-risk and blocked-question safety coverage.

- [ ] **Step 4: Record that Git commit is unavailable in this workspace**

Run: `git -C D:\Desktop\六壬 status --short`

Expected: `fatal: not a git repository (or any of the parent directories): .git`

### Task 3: Verify Auto Classification Through The Realtime Service Contract

**Files:**
- Modify: `D:\Desktop\六壬\tests\test_realtime_service.py`
- Test: `D:\Desktop\六壬\tests\test_realtime_service.py`

- [ ] **Step 1: Write the failing integration tests**

```python
    def test_text_interpret_auto_category_populates_symbols_without_explicit_category(self):
        response = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "这个合作项目能不能推进？",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
                "use_openrouter": False,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["chart"]["category"], "Q-001")
        self.assertEqual(payload["chart"]["rule_trace"]["category_symbols"], ["六合", "朱雀", "勾陈", "青龙"])
        self.assertGreater(len(payload["interpretation"]["entertainment"]["persona_lines"]), 0)

    def test_text_interpret_auto_category_changes_persona_cards_by_question_theme(self):
        relation = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "这段关系是否适合继续？",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
                "use_openrouter": False,
            },
        )
        career = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "这个工作机会适合接吗？",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
                "use_openrouter": False,
            },
        )

        relation_payload = relation.json()
        career_payload = career.json()

        self.assertEqual(relation_payload["chart"]["category"], "Q-002")
        self.assertEqual(career_payload["chart"]["category"], "Q-005")
        self.assertEqual(relation_payload["chart"]["rule_trace"]["category_symbols"], ["天后", "六合", "太阴", "朱雀"])
        self.assertEqual(career_payload["chart"]["rule_trace"]["category_symbols"], ["贵人", "青龙", "朱雀", "勾陈"])

        relation_generals = [
            line["general"] for line in relation_payload["interpretation"]["entertainment"]["persona_lines"]
        ]
        career_generals = [
            line["general"] for line in career_payload["interpretation"]["entertainment"]["persona_lines"]
        ]
        self.assertNotEqual(relation_generals, career_generals)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_service.py -q`

Expected: `FAIL` because the uncategorized requests currently return `chart["category"] == None`, empty `category_symbols`, and the same fallback persona card set.

- [ ] **Step 3: Re-run the integration suite after the `safety.py` change**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_service.py -q`

Expected: `PASS` with the new endpoint assertions green and the pre-existing realtime service contract checks still passing.

- [ ] **Step 4: Run the adjacent frontend contract suite as a final regression check**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_frontend.py -q`

Expected: `PASS`, confirming the backend-only category change did not disturb the existing persona card frontend behavior.

- [ ] **Step 5: Record that Git commit is unavailable in this workspace**

Run: `git -C D:\Desktop\六壬 status --short`

Expected: `fatal: not a git repository (or any of the parent directories): .git`
