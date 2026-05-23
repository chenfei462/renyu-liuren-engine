from __future__ import annotations

import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "template"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "template"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            text = data.strip()
            if text:
                self.text_parts.append(text)


def visible_text(path: Path) -> str:
    parser = _VisibleTextParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return " ".join(parser.text_parts)


def latin_words(text: str) -> list[str]:
    allowed_fragments = {"api"}
    words = re.findall(r"[A-Za-z][A-Za-z0-9+-]*", text)
    return [word for word in words if word.lower() not in allowed_fragments]


class LanguageSwitcherTests(unittest.TestCase):
    def test_realtime_and_release_pages_have_language_switcher(self):
        for path in [
            ROOT / "static" / "realtime" / "index.html",
            ROOT / "static" / "release" / "index.html",
        ]:
            html = path.read_text(encoding="utf-8")
            self.assertIn('class="language-switcher"', html)
            self.assertIn('data-language-current', html)
            self.assertIn('data-language-option="zh"', html)
            self.assertIn('data-language-option="en"', html)
            self.assertIn("/static/realtime/language.js", html)

    def test_default_chinese_pages_do_not_expose_english_ui_words(self):
        for path in [
            ROOT / "static" / "realtime" / "index.html",
            ROOT / "static" / "release" / "index.html",
        ]:
            words = latin_words(visible_text(path))
            self.assertEqual(words, [], f"{path} still exposes English UI words: {words[:12]}")

    def test_language_script_contains_bidirectional_runtime_contract(self):
        script = (ROOT / "static" / "realtime" / "language.js").read_text(encoding="utf-8")
        self.assertIn("localStorage", script)
        self.assertIn("MutationObserver", script)
        self.assertIn("applyRenYuLanguage", script)
        self.assertIn("data-language-option", script)
        self.assertIn("ZH_DYNAMIC", script)
        self.assertIn("EN_DYNAMIC", script)

    def test_language_observer_does_not_rewrite_character_data(self):
        script = (ROOT / "static" / "realtime" / "language.js").read_text(encoding="utf-8")
        self.assertNotIn("characterData: true", script)
        self.assertIn("observer.disconnect()", script)
        self.assertIn("observer.observe(document.body, mutationOptions)", script)
        self.assertLess(script.index("observer.disconnect()"), script.index("callback()"))
        self.assertLess(script.index("callback()"), script.index("observer.observe(document.body, mutationOptions)"))

    def test_language_switcher_runtime_handles_dynamic_nodes_once(self):
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "language_switcher_harness.js")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "Language switcher harness failed\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["afterEnglishClick"]["heading"], "Question")
        business_copy = "针对 Q-001 合作推进：先看三传，再看 Beta 阶段的边界，不要承诺现实结果。"
        self.assertEqual(payload["afterBusinessAppendInEnglish"]["dynamicText"], business_copy)
        self.assertEqual(payload["afterBusinessAppendBackToChinese"]["dynamicText"], business_copy)
        self.assertNotIn("Status information is being prepared", payload["afterBusinessAppendInEnglish"]["dynamicText"])
        self.assertNotIn("状态信息读取中", payload["afterBusinessAppendBackToChinese"]["dynamicText"])
        self.assertEqual(payload["afterDynamicAppend"]["dynamicText"], f"{business_copy}Safety firstLearning material")
        self.assertEqual(payload["afterChineseClick"]["heading"], "本次占问")
        self.assertEqual(payload["afterChineseClick"]["dynamicText"], f"{business_copy}安全边界优先学习资料")
        self.assertLessEqual(payload["afterChineseClick"]["callbackCount"], 6)


if __name__ == "__main__":
    unittest.main()
