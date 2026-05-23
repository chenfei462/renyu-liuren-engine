import json
import os
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine.webapp import app, build_realtime_session_config


class FakeRealtimeClient:
    def __init__(self):
        self.calls = []

    def create_call(self, sdp_offer, session_config):
        self.calls.append({"sdp_offer": sdp_offer, "session_config": session_config})
        return "v=0\r\nmock-answer"


class FakeOpenRouterClient:
    def __init__(self):
        self.calls = []

    def create_chat_completion(self, messages, model=None):
        self.calls.append({"messages": messages, "model": model})
        return {
            "model": model or "deepseek-v4-flash",
            "content": "DeepSeek polished summary",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }


class RealtimeServiceTests(unittest.TestCase):
    def setUp(self):
        self.fake_client = FakeRealtimeClient()
        app.state.realtime_client = self.fake_client
        self.fake_openrouter_client = FakeOpenRouterClient()
        app.state.openrouter_client = self.fake_openrouter_client
        self.client = TestClient(app)

    def test_vercel_entrypoint_exports_fastapi_app(self):
        entrypoint = ROOT / "app.py"
        self.assertTrue(entrypoint.exists())
        spec = importlib.util.spec_from_file_location("vercel_app_entrypoint", entrypoint)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertIs(module.app, app)

    def test_robots_and_sitemap_are_google_crawl_ready(self):
        robots_response = self.client.get("/robots.txt")
        self.assertEqual(robots_response.status_code, 200)
        self.assertIn("text/plain", robots_response.headers["content-type"])
        robots_text = robots_response.text
        self.assertIn("User-agent: *", robots_text)
        self.assertIn("Allow: /", robots_text)
        self.assertIn("Disallow: /api/", robots_text)
        self.assertIn("Sitemap: http://testserver/sitemap.xml", robots_text)

        sitemap_response = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap_response.status_code, 200)
        self.assertIn("application/xml", sitemap_response.headers["content-type"])
        sitemap_xml = sitemap_response.text
        self.assertIn("<loc>http://testserver/</loc>", sitemap_xml)
        self.assertIn("<loc>http://testserver/app</loc>", sitemap_xml)
        self.assertIn("<changefreq>weekly</changefreq>", sitemap_xml)

    def test_public_pages_include_search_metadata(self):
        for path in ["/", "/app"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                html = response.text
                self.assertIn('name="description"', html)
                self.assertIn('name="robots" content="index, follow"', html)
                self.assertIn('rel="canonical"', html)
                self.assertIn('property="og:title"', html)
                self.assertIn('property="og:description"', html)

    def test_health_masks_openai_key(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "sk-secret-value", "DEEPSEEK_API_KEY": "sk-deepseek-secret-value"},
            clear=False,
        ):
            response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["openai_api_key_configured"])
        self.assertTrue(payload["deepseek_api_key_configured"])
        self.assertNotIn("sk-secret-value", json.dumps(payload))
        self.assertNotIn("sk-deepseek-secret-value", json.dumps(payload))
        self.assertEqual(payload["engine"], "ok")
        self.assertEqual(payload["knowledge"], "ok")
        self.assertEqual(payload["openrouter_model"], "deepseek-v4-flash")

    def test_liuren_interpret_endpoint_runs_local_chain(self):
        response = self.client.post(
            "/api/liuren/interpret",
            json={
                "question": "合作项目能不能推进？",
                "datetime": "2026-04-30T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "category": "Q-001",
                "mode": "professional",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("chart", payload)
        self.assertIn("evidence", payload)
        self.assertIn("interpretation", payload)
        self.assertIn("safety", payload)
        self.assertIn("latency_ms", payload)
        self.assertGreaterEqual(payload["interpretation"]["evidence_coverage"]["ratio"], 0.8)

    def test_liuren_interpret_endpoint_accepts_story_and_mentor_modes(self):
        for mode in ["story", "mentor"]:
            with self.subTest(mode=mode):
                response = self.client.post(
                    "/api/liuren/interpret",
                    json={
                        "question": "合作项目能不能推进？",
                        "datetime": "2026-04-30T10:30:00",
                        "timezone": "Asia/Shanghai",
                        "location": "Shanghai",
                        "category": "Q-001",
                        "mode": mode,
                    },
                )

                self.assertEqual(response.status_code, 200)
                payload = response.json()
                self.assertEqual(payload["interpretation"]["mode"], mode)
                self.assertIn("entertainment", payload["interpretation"])

    def test_liuren_interpret_endpoint_validates_required_fields(self):
        response = self.client.post("/api/liuren/interpret", json={"question": "缺字段"})

        self.assertEqual(response.status_code, 422)
        rendered = json.dumps(response.json(), ensure_ascii=False)
        self.assertIn("datetime", rendered)
        self.assertIn("timezone", rendered)

    def test_text_interpret_endpoint_runs_local_chain_and_openrouter_polish(self):
        with patch.dict(os.environ, {"DEEPSEEK_MODEL": "deepseek-v4-flash"}, clear=False):
            response = self.client.post(
                "/api/liuren/text-interpret",
                json={
                    "question": "今天适合推进项目吗？",
                    "datetime": "2026-05-07T10:30:00",
                    "timezone": "Asia/Shanghai",
                    "location": "Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("chart", payload)
        self.assertIn("evidence", payload)
        self.assertIn("interpretation", payload)
        self.assertEqual(payload["openrouter"]["status"], "ok")
        self.assertEqual(payload["openrouter"]["model"], "deepseek-v4-flash")
        self.assertEqual(payload["openrouter"]["content"], "DeepSeek polished summary")
        self.assertEqual(len(self.fake_openrouter_client.calls), 1)
        call = self.fake_openrouter_client.calls[0]
        self.assertEqual(call["model"], "deepseek-v4-flash")
        rendered_messages = json.dumps(call["messages"], ensure_ascii=False)
        self.assertIn("今天适合推进项目吗", rendered_messages)
        self.assertNotIn("sk-deepseek-secret-value", json.dumps(payload))

    def test_plain_text_interpret_returns_learning_materials(self):
        response = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "明天出行是否顺利？",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
                "use_openrouter": False,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        entertainment = payload["interpretation"]["entertainment"]
        self.assertGreater(len(entertainment["persona_lines"]), 0)
        self.assertGreater(len(entertainment["learning_cards"]), 0)
        self.assertIn("share_report", entertainment)

    def test_text_interpret_auto_classifies_collaboration_questions(self):
        response = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "这次合作能不能顺利推进？",
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
        self.assertEqual(
            payload["chart"]["rule_trace"]["category_symbols"],
            ["六合", "朱雀", "勾陈", "青龙"],
        )
        self.assertGreater(len(payload["interpretation"]["entertainment"]["persona_lines"]), 0)

    def test_text_interpret_auto_classification_changes_persona_cards_by_topic(self):
        relationship_response = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "我和他的关系还有机会缓和吗？是否适合主动联系？",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
                "use_openrouter": False,
            },
        )
        work_response = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "这个工作机会是否值得继续争取？",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
                "use_openrouter": False,
            },
        )

        self.assertEqual(relationship_response.status_code, 200)
        self.assertEqual(work_response.status_code, 200)

        relationship_payload = relationship_response.json()
        work_payload = work_response.json()

        self.assertEqual(relationship_payload["chart"]["category"], "Q-002")
        self.assertEqual(
            relationship_payload["chart"]["rule_trace"]["category_symbols"],
            ["天后", "六合", "太阴", "朱雀"],
        )
        self.assertEqual(work_payload["chart"]["category"], "Q-005")
        self.assertEqual(
            work_payload["chart"]["rule_trace"]["category_symbols"],
            ["贵人", "青龙", "朱雀", "勾陈"],
        )

        relationship_persona_generals = [
            line["general"]
            for line in relationship_payload["interpretation"]["entertainment"]["persona_lines"]
        ]
        work_persona_generals = [
            line["general"]
            for line in work_payload["interpretation"]["entertainment"]["persona_lines"]
        ]
        self.assertNotEqual(relationship_persona_generals, work_persona_generals)

    def test_text_interpret_prompt_stays_focused_on_user_question(self):
        response = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "明天出行是否顺利？",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsNotNone(payload["chart"])
        self.assertEqual(payload["openrouter"]["status"], "ok")
        rendered_interpretation = json.dumps(payload["interpretation"], ensure_ascii=False)
        self.assertIn("明天出行是否顺利", rendered_interpretation)
        self.assertIn("出行", rendered_interpretation)
        self.assertEqual(len(self.fake_openrouter_client.calls), 1)
        rendered_messages = json.dumps(self.fake_openrouter_client.calls[0]["messages"], ensure_ascii=False)
        self.assertIn("明天出行是否顺利", rendered_messages)
        self.assertIn("第一句必须围绕用户原问题", rendered_messages)
        self.assertIn("不要只输出通用产品说明", rendered_messages)

    def test_text_interpret_rejects_non_liuren_questions_without_deepseek(self):
        response = self.client.post(
            "/api/liuren/text-interpret",
            json={
                "question": "明天天气如何",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsNone(payload["chart"])
        self.assertEqual(payload["evidence"], [])
        self.assertEqual(payload["openrouter"]["status"], "skipped")
        self.assertIn("non_liuren_question", payload["interpretation"]["blocked_reasons"])
        self.assertIn("只用于具体事项占问", payload["interpretation"]["overview"])
        self.assertEqual(len(self.fake_openrouter_client.calls), 0)

    def test_liuren_interpret_rejects_non_liuren_questions(self):
        response = self.client.post(
            "/api/liuren/interpret",
            json={
                "question": "明天天气如何",
                "datetime": "2026-05-07T10:30:00",
                "timezone": "Asia/Shanghai",
                "location": "Shanghai",
                "mode": "plain",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsNone(payload["chart"])
        self.assertEqual(payload["evidence"], [])
        self.assertIn("non_liuren_question", payload["interpretation"]["blocked_reasons"])
        self.assertIn("明天出行是否顺利", payload["interpretation"]["action_prompts"][0])

    def test_text_interpret_obeys_ops_pause_guard(self):
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch.dict(os.environ, {"LIUREN_OPS_EVENTS_PATH": str(Path(tmpdir) / "ops_events.jsonl")}),
            patch("liuren_engine.webapp.is_liuren_question", return_value=True),
        ):
            self.client.post("/api/ops/pause", json={"reason": "test pause"})
            tool_response = self.client.post(
                "/api/liuren/interpret",
                json={
                    "question": "test question",
                    "datetime": "2026-04-30T10:30:00",
                    "timezone": "Asia/Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                },
            )
            text_response = self.client.post(
                "/api/liuren/text-interpret",
                json={
                    "question": "test question",
                    "datetime": "2026-04-30T10:30:00",
                    "timezone": "Asia/Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                },
            )

        self.assertEqual(tool_response.status_code, 200)
        self.assertEqual(text_response.status_code, 200)
        tool_payload = tool_response.json()
        text_payload = text_response.json()
        self.assertIsNone(tool_payload["chart"])
        self.assertIsNone(text_payload["chart"])
        self.assertEqual(text_payload["interpretation"]["blocked_reasons"], tool_payload["interpretation"]["blocked_reasons"])
        self.assertIn("ops_paused", text_payload["interpretation"]["blocked_reasons"])
        self.assertEqual(text_payload["openrouter"]["status"], "skipped")
        self.assertEqual(len(self.fake_openrouter_client.calls), 0)

    def test_text_interpret_obeys_public_pause_guard(self):
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch.dict(
                os.environ,
                {
                    "LIUREN_PUBLIC_SESSION_LOG_PATH": str(Path(tmpdir) / "public_sessions.jsonl"),
                    "LIUREN_PUBLIC_INCIDENTS_PATH": str(Path(tmpdir) / "public_incidents.jsonl"),
                    "LIUREN_GROWTH_EVENTS_PATH": str(Path(tmpdir) / "growth.jsonl"),
                    "LIUREN_OPS_EVENTS_PATH": str(Path(tmpdir) / "ops.jsonl"),
                },
            ),
            patch("liuren_engine.webapp.is_liuren_question", return_value=True),
        ):
            self.client.post(
                "/api/public/incident",
                json={"event_type": "high_risk_leak", "severity": "P1", "summary": "pause public"},
            )
            tool_response = self.client.post(
                "/api/liuren/interpret",
                json={
                    "question": "test question",
                    "datetime": "2026-04-30T12:00:00+08:00",
                    "timezone": "Asia/Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                },
            )
            text_response = self.client.post(
                "/api/liuren/text-interpret",
                json={
                    "question": "test question",
                    "datetime": "2026-04-30T12:00:00+08:00",
                    "timezone": "Asia/Shanghai",
                    "category": "Q-001",
                    "mode": "plain",
                },
            )

        self.assertEqual(tool_response.status_code, 200)
        self.assertEqual(text_response.status_code, 200)
        tool_payload = tool_response.json()
        text_payload = text_response.json()
        self.assertIsNone(tool_payload["chart"])
        self.assertIsNone(text_payload["chart"])
        self.assertEqual(text_payload["interpretation"]["blocked_reasons"], tool_payload["interpretation"]["blocked_reasons"])
        self.assertIn("public_paused", text_payload["interpretation"]["blocked_reasons"])
        self.assertEqual(text_payload["openrouter"]["status"], "skipped")
        self.assertEqual(len(self.fake_openrouter_client.calls), 0)

    def test_high_risk_tool_response_is_safety_only(self):
        response = self.client.post(
            "/api/liuren/interpret",
            json={
                "question": "我该不该买这只股票？",
                "datetime": "2026-04-30T10:30:00",
                "timezone": "Asia/Shanghai",
                "category": "Q-011",
                "mode": "professional",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["safety"]["action"], "safety_only")
        self.assertEqual(payload["interpretation"]["plain_explanation"], [])

    def test_realtime_session_uses_mocked_client_and_does_not_return_api_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-real-server-key"}, clear=False):
            response = self.client.post(
                "/api/realtime/session",
                content="v=0\r\nmock-offer",
                headers={"Content-Type": "application/sdp"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "v=0\r\nmock-answer")
        self.assertNotIn("sk-real-server-key", response.text)
        self.assertEqual(self.fake_client.calls[0]["sdp_offer"], "v=0\r\nmock-offer")
        config = self.fake_client.calls[0]["session_config"]
        self.assertEqual(config["model"], "gpt-realtime")
        self.assertEqual(config["audio"]["output"]["voice"], "marin")
        tool_names = [tool["name"] for tool in config["tools"]]
        self.assertEqual(tool_names, ["create_liuren_interpretation"])
        mode_enum = config["tools"][0]["parameters"]["properties"]["mode"]["enum"]
        self.assertEqual(mode_enum, ["professional", "plain", "story", "mentor"])

    def test_realtime_session_config_locks_prompt_and_tool_schema(self):
        config = build_realtime_session_config()
        rendered = json.dumps(config, ensure_ascii=False)

        self.assertIn("不得自行排盘", config["instructions"])
        self.assertIn("不得伪造出处", config["instructions"])
        self.assertIn("故事版是娱乐表达", config["instructions"])
        self.assertIn("导师版是学习解释", config["instructions"])
        self.assertIn("safety_validation", config["instructions"])
        self.assertIn("blocked_reasons", config["instructions"])
        self.assertIn("create_liuren_interpretation", rendered)
        self.assertEqual(config["tool_choice"], "auto")
        self.assertEqual(config["audio"]["input"]["turn_detection"]["type"], "semantic_vad")


if __name__ == "__main__":
    unittest.main()
