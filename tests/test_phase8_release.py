import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine.release import build_release_metrics, build_release_readiness, load_launch_checklist, load_release_config
from liuren_engine.webapp import app


class PhaseEightReleaseTests(unittest.TestCase):
    def test_release_config_freezes_low_risk_mvp_scope(self):
        config = load_release_config(ROOT)

        self.assertEqual(config["release_id"], "release_config.v0.1")
        self.assertEqual(config["status"], "limited_mvp_release_candidate")
        self.assertEqual(config["allowed_modes"], ["professional", "plain", "story", "mentor"])
        self.assertIn("Q-001", config["allowed_categories"])
        self.assertIn("Q-014", config["allowed_categories"])
        for category in ["Q-009", "Q-010", "Q-011", "Q-012"]:
            self.assertNotIn(category, config["allowed_categories"])
            self.assertIn(category, config["blocked_categories"])
        self.assertIn("privacy", config["legal_documents"])
        self.assertIn("不构成现实建议", config["release_notice"])

    def test_release_readiness_blocks_when_review_or_safety_items_remain(self):
        readiness = build_release_readiness(
            root=ROOT,
            beta_report={
                "feedback_count": 2,
                "safety_block_count": 1,
                "manual_review_items": [{"chart_id": "chart_blocked", "blocked_reasons": ["safety_issue"]}],
                "realtime_tool_bypass_count": 0,
                "hallucination_incident_count": 0,
            },
            expert_review={"cases": [{"case_id": "ER-BIYONG-001", "approved_for_beta": False, "review_status": "needs_expert_review"}]},
            copyright_review={"items": [{"item_id": "CR-005", "beta_status": "blocked", "in_user_visible_product": True}]},
            red_team_passed=True,
            golden_cases_passed=True,
        )

        self.assertEqual(readiness["readiness_id"], "release_readiness.v0.1")
        self.assertEqual(readiness["release_status"], "blocked")
        self.assertIn("beta_safety_blocks_pending", readiness["blocked_reasons"])
        self.assertIn("expert_review_pending", readiness["blocked_reasons"])
        self.assertIn("copyright_blocked_visible", readiness["blocked_reasons"])
        self.assertIn("Q-001", readiness["allowed_for_mvp"]["categories"])
        self.assertIn("Q-011", readiness["blocked_for_mvp"]["categories"])
        self.assertIn("biyong", readiness["needs_expert_review"]["rules"])

    def test_release_metrics_summarize_beta_report_for_launch_monitoring(self):
        metrics = build_release_metrics(
            root=ROOT,
            beta_report={
                "session_count": 5,
                "completion_count": 3,
                "feedback_count": 4,
                "mode_distribution": {"plain": 2, "story": 1, "mentor": 1},
                "feedback_distribution": {"helpful": 2, "voice_issue": 1, "safety_issue": 1},
                "safety_block_count": 1,
                "high_risk_trigger_count": 2,
                "failed_interface_count": 1,
                "manual_review_items": [{"chart_id": "chart_review"}],
            },
        )

        self.assertEqual(metrics["metrics_id"], "release_metrics.v0.1")
        self.assertEqual(metrics["session_count"], 5)
        self.assertEqual(metrics["completion_rate"], 0.6)
        self.assertEqual(metrics["mode_distribution"]["story"], 1)
        self.assertEqual(metrics["safety_block_count"], 1)
        self.assertEqual(metrics["manual_review_count"], 1)

    def test_release_and_legal_api_endpoints(self):
        client = TestClient(app)
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(os.environ, {"LIUREN_BETA_FEEDBACK_PATH": str(Path(tmpdir) / "feedback.jsonl")}):
            config = client.get("/api/release/config")
            self.assertEqual(config.status_code, 200)
            self.assertEqual(config.json()["release_id"], "release_config.v0.1")

            readiness = client.get("/api/release/readiness")
            self.assertEqual(readiness.status_code, 200)
            self.assertIn(readiness.json()["release_status"], {"ready", "blocked"})

            metrics = client.get("/api/release/metrics")
            self.assertEqual(metrics.status_code, 200)
            self.assertEqual(metrics.json()["metrics_id"], "release_metrics.v0.1")

            for path, expected in [
                ("/api/legal/privacy", "不保存用户录音"),
                ("/api/legal/safety", "不构成现实建议"),
                ("/api/legal/copyright", "摘要、定位和规则化转写"),
            ]:
                response = client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(expected, response.json()["content"])

    def test_release_homepage_links_to_app_and_legal_documents(self):
        client = TestClient(app)
        home = client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn("壬语", home.text)
        self.assertIn("传统文化学习与娱乐体验", home.text)
        self.assertIn('href="/app"', home.text)
        self.assertIn('href="/api/legal/privacy"', home.text)
        self.assertIn('id="releaseScope"', home.text)

        app_page = client.get("/app")
        self.assertEqual(app_page.status_code, 200)
        self.assertIn('id="connectBtn"', app_page.text)

    def test_release_homepage_uses_trust_entry_layout(self):
        html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "static" / "release" / "styles.css").read_text(encoding="utf-8")

        for snippet in [
            'class="release-shell trust-entry"',
            'class="release-nav"',
            'class="hero-grid"',
            'class="product-preview"',
            'class="trust-strip"',
            'id="mvpScope"',
            'id="safetyBoundary"',
            'id="launchStatus"',
            'id="finalCta"',
            'href="/app"',
            'href="/api/release/readiness"',
            "澹语 · 大六壬",
            "大六壬实时解读的文化学习入口",
            "不构成现实建议",
        ]:
            self.assertIn(snippet, html)

        self.assertLess(html.index('class="hero-grid"'), html.index('class="trust-strip"'))
        self.assertLess(html.index('id="mvpScope"'), html.index('id="launchStatus"'))
        self.assertLess(html.index('id="safetyBoundary"'), html.index('id="finalCta"'))

        for rule in [
            ".hero-grid",
            ".product-preview",
            ".trust-strip",
            ".status-grid",
            "@media (max-width: 900px)",
            "focus-visible",
            "prefers-reduced-motion",
        ]:
            self.assertIn(rule, css)

    def test_release_status_board_is_a_real_path_panel(self):
        html = (ROOT / "static" / "release" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "static" / "release" / "styles.css").read_text(encoding="utf-8")

        for snippet in [
            'id="releaseStatusOverview"',
            'id="releaseGateBadge"',
            'id="releaseMetricStrip"',
            'id="releaseBlockerList"',
            'id="releaseNextActionList"',
            'id="releasePhasePath"',
            'id="releasePathLinks"',
            'id="opsStatusMeta"',
            'id="phase15PaymentMeta"',
            'src="/static/release/app.js"',
            'href="/api/phase11/report"',
            'href="/api/phase15/report"',
        ]:
            self.assertIn(snippet, html)

        for rule in [
            ".status-overview",
            ".phase-path",
            ".phase-step",
            ".metric-strip",
            ".blocker-list",
            ".status-actions",
        ]:
            self.assertIn(rule, css)

    def test_release_status_runtime_localizes_api_enums_and_payloads(self):
        app_js = ROOT / "static" / "release" / "app.js"
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(app_js))}, "utf8");

function stripTags(value) {{
  return String(value).replace(/<[^>]*>/g, " ").replace(/\\s+/g, " ").trim();
}}

function createClassList() {{
  const names = new Set();
  return {{
    add(name) {{ names.add(name); }},
    remove(name) {{ names.delete(name); }},
    toggle(name, force) {{
      if (force) names.add(name);
      else names.delete(name);
      return !!force;
    }},
    contains(name) {{ return names.has(name); }},
  }};
}}

function createElement(id) {{
  let html = "";
  let text = "";
  return {{
    id,
    dataset: {{}},
    attributes: {{}},
    classList: createClassList(),
    get innerHTML() {{ return html; }},
    set innerHTML(value) {{ html = String(value); text = stripTags(value); }},
    get textContent() {{ return text; }},
    set textContent(value) {{ text = String(value); html = String(value); }},
    setAttribute(name, value) {{ this.attributes[name] = String(value); }},
    getAttribute(name) {{ return this.attributes[name] || null; }},
    querySelectorAll() {{ return []; }},
  }};
}}

const elementIds = [
  "releaseGateBadge",
  "releaseStatusSummary",
  "releaseMetricStrip",
  "releaseBlockerList",
  "releaseNextActionList",
  "releasePhasePath",
  "releasePathLinks",
  "opsStatusText",
  "opsStatusMeta",
  "canaryStatusText",
  "canaryStatusMeta",
  "contentCalendarList",
  "phase11CanaryText",
  "phase11CanaryMeta",
  "phase12PublicText",
  "phase12PublicMeta",
  "phase13ProductizationText",
  "phase13ProductizationMeta",
  "phase14MonetizationText",
  "phase14MonetizationMeta",
  "phase15PaymentText",
  "phase15PaymentMeta",
];
const elements = Object.fromEntries(elementIds.map((id) => [id, createElement(id)]));

const document = {{
  documentElement: {{ dataset: {{ language: "zh" }} }},
  listeners: {{}},
  getElementById(id) {{ return elements[id] || null; }},
  addEventListener(type, handler) {{
    this.listeners[type] = this.listeners[type] || [];
    this.listeners[type].push(handler);
  }},
  dispatchEvent(event) {{
    for (const handler of this.listeners[event.type] || []) handler(event);
  }},
}};

const localStorage = {{
  value: "zh",
  getItem() {{ return this.value; }},
  setItem(key, value) {{ this.value = String(value); }},
}};

const payloads = {{
  "/api/release/readiness": {{
    release_status: "blocked",
    blocked_reasons: ["beta_manual_review_pending", "expert_review_pending", "payment_provider_blocked"],
    needs_expert_review: {{ case_count: 12 }},
    allowed_for_mvp: {{ categories: ["Q-001", "Q-014"] }},
  }},
  "/api/ops/status": {{
    status: "blocked",
    notice: "Ops is blocked",
    blocked_reasons: ["expert_review_pending"],
    pause_reason: "release_readiness_blocked",
    allowed_tester_count: 50,
    review_queue: {{ case_count: 12 }},
    canary_gate: {{ canary_allowed: false, blocked_rules: ["biyong"] }},
  }},
  "/api/canary/config": {{ invite_required: true, tester_user_limit: 50 }},
  "/api/content/calendar": {{
    items: [
      {{ content_id: "CC-003", column: "古籍拆读", title: "出处卡怎样变成可审校规则", status: "草稿" }},
    ],
  }},
  "/api/canary/metrics": {{
    session_count: 2,
    returning_tester_count: 1,
    feedback_submit_count: 1,
    share_report_count: 0,
  }},
  "/api/public-release/gate": {{
    gate_status: "blocked",
    blocked_reasons: ["insufficient_canary_sessions"],
    next_step: "return_to_canary_or_review_fix",
  }},
  "/api/public/status": {{
    launch_status: "blocked",
    blocked_reasons: ["public_release_gate_blocked"],
  }},
  "/api/public/metrics": {{
    session_count: 3,
    feedback_submit_count: 1,
    critical_incident_count: 0,
  }},
  "/api/productization/gate": {{
    gate_status: "blocked",
    blocked_reasons: ["public_mvp_not_active"],
    next_step: "return_to_public_launch_fix",
  }},
  "/api/product/metrics": {{
    visitor_count: 4,
    completed_node_count: 1,
    returning_visitor_count: 1,
  }},
  "/api/monetization/gate": {{
    gate_status: "blocked",
    blocked_reasons: ["productization_not_active"],
    next_step: "return_to_productization_fix",
  }},
  "/api/monetization/metrics": {{
    event_count: 5,
    business_lead_count: 1,
    member_interest_count: 2,
    offer_click_count: 1,
  }},
  "/api/payment/gate": {{
    gate_status: "blocked",
    blocked_reasons: ["insufficient_monetization_interest"],
    enabled_capabilities: [],
    next_step: "return_to_monetization_fix",
  }},
  "/api/payment/metrics": {{
    order_count: 1,
    refund_case_count: 0,
    paid_sandbox_count: 0,
    blocked_order_count: 1,
  }},
}};

const fetchCalls = [];
async function fetch(url) {{
  fetchCalls.push(url);
  if (!payloads[url]) throw new Error(`Unexpected URL ${{url}}`);
  return {{ ok: true, status: 200, json: async () => payloads[url] }};
}}

const context = {{ console, document, localStorage, fetch, window: null, Intl, Promise, setTimeout, clearTimeout }};
context.window = context;
context.globalThis = context;

async function flushAsync() {{
  for (let index = 0; index < 8; index += 1) {{
    await Promise.resolve();
  }}
  await new Promise((resolve) => setTimeout(resolve, 0));
}}

async function main() {{
  vm.createContext(context);
  vm.runInContext(source, context);
  document.dispatchEvent({{ type: "DOMContentLoaded" }});
  await flushAsync();
  const zhText = Object.values(elements).map((element) => element.textContent).join(" ");

  document.documentElement.dataset.language = "en";
  localStorage.value = "en";
  document.dispatchEvent({{ type: "renyu:languagechange", detail: {{ language: "en" }} }});
  await flushAsync();
  const enText = Object.values(elements).map((element) => element.textContent).join(" ");

  process.stdout.write(JSON.stringify({{ zhText, enText, fetchCalls }}));
}}

main().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
        result = subprocess.run(
            ["node", "-"],
            input=harness,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "Release status harness failed\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        payload = json.loads(result.stdout)

        self.assertIn("内测人工复核仍有待处理", payload["zhText"])
        self.assertIn("未识别的后端状态", payload["zhText"])
        self.assertIn("支付沙箱", payload["zhText"])
        self.assertIn("出处卡怎样变成可审校规则", payload["zhText"])
        self.assertNotRegex(payload["zhText"], r"\b(blocked|Canary|Payment|Productization|Monetization|sessions|expert_review_pending|insufficient_canary_sessions|payment_provider_blocked)\b")
        self.assertIn("Beta manual review is still pending", payload["enText"])
        self.assertIn("Payment sandbox", payload["enText"])
        self.assertIn("Unknown backend state", payload["enText"])
        self.assertIn("How source cards become reviewable rules", payload["enText"])
        self.assertNotRegex(payload["enText"], r"[\u4e00-\u9fff]")
        for endpoint in [
            "/api/release/readiness",
            "/api/ops/status",
            "/api/canary/config",
            "/api/content/calendar",
            "/api/canary/metrics",
            "/api/public-release/gate",
            "/api/public/status",
            "/api/public/metrics",
            "/api/productization/gate",
            "/api/product/metrics",
            "/api/monetization/gate",
            "/api/monetization/metrics",
            "/api/payment/gate",
            "/api/payment/metrics",
        ]:
            self.assertIn(endpoint, payload["fetchCalls"])

    def test_launch_checklist_and_schema_files_exist(self):
        checklist = load_launch_checklist(ROOT)

        self.assertEqual(checklist["checklist_id"], "launch_checklist.v0.1")
        self.assertGreaterEqual(len(checklist["commands"]), 5)
        self.assertIn("red_team", {item["check_id"] for item in checklist["checks"]})
        for schema_name in [
            "release_config.response.schema.json",
            "release_readiness.response.schema.json",
            "release_metrics.response.schema.json",
            "legal_document.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")

    def test_pricing_and_launch_copy_avoid_forbidden_promises(self):
        combined = "\n".join(
            (ROOT / "docs" / doc_name).read_text(encoding="utf-8")
            for doc_name in [
                "pricing_strategy.v0.1.md",
                "phase8_handoff.v0.1.md",
                "user_notice.v0.1.md",
            ]
        )
        for forbidden in ["包赢", "必赚", "确诊", "用药", "胜诉", "准确率保证"]:
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
