import json
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

import re


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "static" / "realtime" / "app.js"


class _HtmlIdStructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, str | None]] = []
        self.by_id: dict[str, dict[str, object]] = {}

    def _record_id(self, tag: str, element_id: str) -> None:
        ancestor_ids = [ancestor_id for _, ancestor_id in self.stack if ancestor_id]
        parent_id = next((ancestor_id for _, ancestor_id in reversed(self.stack) if ancestor_id), None)
        self.by_id[element_id] = {
            "tag": tag,
            "ancestor_ids": ancestor_ids,
            "parent_id": parent_id,
        }

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        element_id = attrs_dict.get("id")
        if element_id:
            self._record_id(tag, element_id)
        self.stack.append((tag, element_id))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        element_id = attrs_dict.get("id")
        if element_id:
            self._record_id(tag, element_id)

    def handle_endtag(self, tag: str) -> None:
        while self.stack:
            start_tag, _ = self.stack.pop()
            if start_tag == tag:
                break


def parse_html_id_structure(html: str) -> dict[str, dict[str, object]]:
    parser = _HtmlIdStructureParser()
    parser.feed(html)
    return parser.by_id


def run_realtime_harness(script: str) -> dict:
    result = subprocess.run(
        ["node", "-"],
        input=script,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "Node harness failed\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return json.loads(result.stdout)


class RealtimeFrontendContractTests(unittest.TestCase):
    def run_nav_click_harness(self, href: str) -> dict:
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(APP_JS))}, "utf8");

function createClassList(initial = []) {{
  const set = new Set(initial);
  return {{
    add(name) {{
      set.add(name);
    }},
    remove(name) {{
      set.delete(name);
    }},
    toggle(name, force) {{
      if (force === undefined) {{
        if (set.has(name)) {{
          set.delete(name);
          return false;
        }}
        set.add(name);
        return true;
      }}
      if (force) {{
        set.add(name);
      }} else {{
        set.delete(name);
      }}
      return !!force;
    }},
    contains(name) {{
      return set.has(name);
    }},
    toArray() {{
      return Array.from(set).sort();
    }},
  }};
}}

function createElement(id, tagName = "div") {{
  let innerHtml = "";
  let textValue = "";
  return {{
    id,
    tagName: tagName.toUpperCase(),
    value: "",
    disabled: false,
    open: false,
    dataset: {{}},
    attributes: {{}},
    classList: createClassList(),
    listeners: {{}},
    get innerHTML() {{
      return innerHtml;
    }},
    set innerHTML(value) {{
      innerHtml = String(value);
      textValue = String(value);
    }},
    get textContent() {{
      return textValue;
    }},
    set textContent(value) {{
      textValue = String(value);
      innerHtml = String(value);
    }},
    addEventListener(type, handler) {{
      this.listeners[type] = handler;
    }},
    scrollIntoView(options) {{
      this.scrollOptions = options;
    }},
    setAttribute(name, value) {{
      this.attributes[name] = String(value);
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        this.dataset[key] = String(value);
      }}
    }},
    getAttribute(name) {{
      if (Object.prototype.hasOwnProperty.call(this.attributes, name)) {{
        return this.attributes[name];
      }}
      return null;
    }},
    removeAttribute(name) {{
      delete this.attributes[name];
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        delete this.dataset[key];
      }}
    }},
  }};
}}

const elementIds = [
  "connectBtn",
  "disconnectBtn",
  "interruptBtn",
  "modeSelect",
  "testerId",
  "inviteCode",
  "status",
  "textQuestion",
  "runTextInterpretBtn",
  "textInterpretStatus",
  "betaNotice",
  "opsPauseNotice",
  "publicFeedbackNotice",
  "visitorNickname",
  "saveVisitorProfileBtn",
  "visitorProfileStatus",
  "transcript",
  "toolLog",
  "interpretationPreview",
  "explainResult",
  "debugDetails",
  "debugJson",
  "learningMaterials",
  "personaCards",
  "personaCardsToggle",
  "learningCards",
  "safetyState",
  "feedbackType",
  "feedbackNote",
  "submitFeedbackBtn",
  "feedbackStatus",
  "canaryTaskList",
  "commercialInterest",
  "commercialInterestStatus",
  "offerCatalogList",
  "monetizationStatus",
  "businessLeadNickname",
  "businessLeadChannel",
  "businessLeadSummary",
  "submitBusinessLeadBtn",
  "businessLeadStatus",
  "membershipTiersList",
  "paymentGateStatus",
  "paymentTierSelect",
  "startSandboxCheckoutBtn",
  "confirmSandboxPaymentBtn",
  "failSandboxPaymentBtn",
  "cancelSandboxOrderBtn",
  "refundSandboxOrderBtn",
  "sandboxOrderStatus",
  "shareReport",
  "reportText",
  "pdfReportDraft",
  "remoteAudio",
  "questionPanel",
  "learningPathPanel",
  "supportPanel",
  "feedbackPanel",
  "experimentsPanel",
];

const elements = Object.fromEntries(elementIds.map((id) => [id, createElement(id)]));
elements.modeSelect.value = "plain";
elements.feedbackType.value = "general";

const navLinks = {{
  "#questionPanel": createElement("navQuestion", "a"),
  "#learningPathPanel": createElement("navLearningPath", "a"),
  "#feedbackPanel": createElement("navFeedback", "a"),
  "#experimentsPanel": createElement("navExperiments", "a"),
}};

for (const [anchorHref, link] of Object.entries(navLinks)) {{
  link.href = anchorHref;
  link.setAttribute("href", anchorHref);
}}
navLinks["#questionPanel"].setAttribute("aria-current", "page");

const navLinkList = Object.values(navLinks);
const monetizationButtons = [];

const document = {{
  getElementById(id) {{
    return elements[id] || null;
  }},
  querySelector(selector) {{
    if (selector in navLinks) {{
      return navLinks[selector];
    }}
    return null;
  }},
  querySelectorAll(selector) {{
    if (selector === ".monetizationInterest") {{
      return monetizationButtons;
    }}
    if (selector === ".app-nav a") {{
      return navLinkList;
    }}
    return [];
  }},
}};

const fetchStub = async () => ({{ ok: true, json: async () => ({{}}), text: async () => "" }});

const context = {{
  console,
  document,
  window: null,
  fetch: fetchStub,
  navigator: {{ mediaDevices: {{ getUserMedia: async () => ({{ getTracks: () => [] }}) }} }},
  RTCPeerConnection: function RTCPeerConnection() {{
    return {{
      addTrack() {{}},
      createDataChannel() {{ return {{ addEventListener() {{}}, close() {{}}, readyState: "open" }}; }},
      createOffer: async () => ({{ sdp: "stub" }}),
      setLocalDescription: async () => {{}},
      setRemoteDescription: async () => {{}},
      close() {{}},
    }};
  }},
  Intl,
  Date,
  JSON,
  setTimeout,
  clearTimeout,
}};
context.window = context;
context.globalThis = context;

vm.createContext(context);
vm.runInContext(source, context);

const clickedHref = {json.dumps(href)};
const link = navLinks[clickedHref];
let preventedDefault = false;
const hasClickHandler = typeof link?.listeners?.click === "function";
if (hasClickHandler) {{
  link.listeners.click({{
    currentTarget: link,
    preventDefault() {{
      preventedDefault = true;
    }},
  }});
}}

function currentHref() {{
  for (const [anchorHref, navLink] of Object.entries(navLinks)) {{
    if (navLink.getAttribute("aria-current") === "page") {{
      return anchorHref;
    }}
  }}
  return null;
}}

process.stdout.write(JSON.stringify({{
  hasClickHandler,
  preventedDefault,
  linkCurrentHref: currentHref(),
  questionPanelScrollOptions: elements.questionPanel.scrollOptions || null,
  learningPathOpen: elements.learningPathPanel.open,
  learningPathScrollOptions: elements.learningPathPanel.scrollOptions || null,
  experimentsOpen: elements.experimentsPanel.open,
  experimentsScrollOptions: elements.experimentsPanel.scrollOptions || null,
  supportPanelScrollOptions: elements.supportPanel.scrollOptions || null,
  feedbackPanelScrollOptions: elements.feedbackPanel.scrollOptions || null,
  questionActiveClass: elements.questionPanel.classList.toArray(),
  learningPathActiveClass: elements.learningPathPanel.classList.toArray(),
  feedbackActiveClass: elements.feedbackPanel.classList.toArray(),
  experimentsActiveClass: elements.experimentsPanel.classList.toArray(),
  questionActiveState: elements.questionPanel.dataset.navActive || null,
  learningPathActiveState: elements.learningPathPanel.dataset.navActive || null,
  feedbackActiveState: elements.feedbackPanel.dataset.navActive || null,
  experimentsActiveState: elements.experimentsPanel.dataset.navActive || null,
}}));
"""
        return run_realtime_harness(harness)

    def run_share_report_harness(
        self,
        report_payload: dict,
        trigger_copy_action: str | None = None,
        trigger_canary_action: str | None = None,
    ) -> dict:
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(APP_JS))}, "utf8");
const reportPayload = {json.dumps(report_payload)};
const triggerCopyAction = {json.dumps(trigger_copy_action)};
const triggerCanaryAction = {json.dumps(trigger_canary_action)};

function createClassList(initial = []) {{
  const set = new Set(initial);
  return {{
    add(name) {{
      set.add(name);
    }},
    remove(name) {{
      set.delete(name);
    }},
    toggle(name, force) {{
      if (force === undefined) {{
        if (set.has(name)) {{
          set.delete(name);
          return false;
        }}
        set.add(name);
        return true;
      }}
      if (force) {{
        set.add(name);
      }} else {{
        set.delete(name);
      }}
      return !!force;
    }},
    contains(name) {{
      return set.has(name);
    }},
    toArray() {{
      return Array.from(set).sort();
    }},
  }};
}}

function createElement(id, tagName = "div") {{
  let innerHtml = "";
  let textValue = "";
  return {{
    id,
    tagName: tagName.toUpperCase(),
    value: "",
    disabled: false,
    open: false,
    dataset: {{}},
    attributes: {{}},
    style: {{}},
    className: "",
    classList: createClassList(),
    listeners: {{}},
    get innerHTML() {{
      return innerHtml;
    }},
    set innerHTML(value) {{
      innerHtml = String(value);
      textValue = String(value);
    }},
    get textContent() {{
      return textValue;
    }},
    set textContent(value) {{
      textValue = String(value);
      innerHtml = String(value);
    }},
    addEventListener(type, handler) {{
      this.listeners[type] = handler;
    }},
    scrollIntoView(options) {{
      this.scrollOptions = options;
    }},
    focus() {{
      this.focused = true;
    }},
    setAttribute(name, value) {{
      this.attributes[name] = String(value);
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        this.dataset[key] = String(value);
      }}
    }},
    getAttribute(name) {{
      if (Object.prototype.hasOwnProperty.call(this.attributes, name)) {{
        return this.attributes[name];
      }}
      return null;
    }},
    removeAttribute(name) {{
      delete this.attributes[name];
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        delete this.dataset[key];
      }}
    }},
  }};
}}

const elementIds = [
  "connectBtn",
  "disconnectBtn",
  "interruptBtn",
  "modeSelect",
  "testerId",
  "inviteCode",
  "status",
  "textQuestion",
  "runTextInterpretBtn",
  "textInterpretStatus",
  "betaNotice",
  "opsPauseNotice",
  "publicFeedbackNotice",
  "visitorNickname",
  "saveVisitorProfileBtn",
  "visitorProfileStatus",
  "transcript",
  "toolLog",
  "interpretationPreview",
  "explainResult",
  "debugDetails",
  "debugJson",
  "learningMaterials",
  "personaCards",
  "personaCardsToggle",
  "learningCards",
  "learningPathPanel",
  "learningPathSummary",
  "learningPathRecommended",
  "learningPathNodes",
  "learningPathDetail",
  "learningPathStatus",
  "safetyState",
  "feedbackType",
  "feedbackNote",
  "submitFeedbackBtn",
  "feedbackStatus",
  "canaryTaskList",
  "commercialInterest",
  "commercialInterestSummary",
  "commercialInterestStatus",
  "monetizationGateBadge",
  "monetizationMetricsHeadline",
  "monetizationOverview",
  "monetizationReasonList",
  "monetizationMetricsList",
  "offerCatalogList",
  "monetizationStatus",
  "commercialPathSteps",
  "commercialPathSummary",
  "commercialPathMetrics",
  "businessLeadNickname",
  "businessLeadChannel",
  "businessLeadSummary",
  "submitBusinessLeadBtn",
  "businessLeadStatus",
  "businessLeadOutcome",
  "membershipTiersList",
  "paymentGateStatus",
  "paymentGateBadge",
  "paymentGateReasonList",
  "paymentCapabilitiesList",
  "paymentMetricsList",
  "paymentTierSelect",
  "startSandboxCheckoutBtn",
  "confirmSandboxPaymentBtn",
  "failSandboxPaymentBtn",
  "cancelSandboxOrderBtn",
  "refundSandboxOrderBtn",
  "sandboxOrderStatus",
  "sandboxOrderDetail",
  "shareReport",
  "shareReportMeta",
  "shareReportLead",
  "shareReportCards",
  "shareReportCopyStatus",
  "copyShareReportTextBtn",
  "copyShareReportHtmlBtn",
  "shareReportDraftDetails",
  "shareReportDraftMeta",
  "shareReportDraftCards",
  "copyShareReportDraftBtn",
  "remoteAudio",
  "questionPanel",
  "feedbackPanel",
  "experimentsPanel",
];

const elements = Object.fromEntries(
  elementIds.map((id) => [
    id,
    createElement(
      id,
      id === "experimentsPanel" || id === "shareReportDraftDetails" ? "details" : id.startsWith("copy") ? "button" : "div",
    ),
  ]),
);
elements.modeSelect.value = "plain";
elements.feedbackType.value = "helpful";

const clipboardWrites = [];
const document = {{
  getElementById(id) {{
    return elements[id] || null;
  }},
  querySelector() {{
    return null;
  }},
  querySelectorAll(selector) {{
    if (selector === ".monetizationInterest") {{
      return [];
    }}
    if (selector === ".app-nav a") {{
      return [];
    }}
    return [];
  }},
}};

const fetchStub = async () => ({{ ok: true, status: 200, json: async () => ({{}}), text: async () => "" }});

const context = {{
  console,
  document,
  window: null,
  fetch: fetchStub,
  navigator: {{
    mediaDevices: {{ getUserMedia: async () => ({{ getTracks: () => [] }}) }},
    clipboard: {{
      writeText: async (value) => {{
        clipboardWrites.push(String(value));
      }},
    }},
  }},
  RTCPeerConnection: function RTCPeerConnection() {{
    return {{
      addTrack() {{}},
      createDataChannel() {{ return {{ addEventListener() {{}}, close() {{}}, readyState: "open" }}; }},
      createOffer: async () => ({{ sdp: "stub" }}),
      setLocalDescription: async () => {{}},
      setRemoteDescription: async () => {{}},
      close() {{}},
    }};
  }},
  Intl,
  Date,
  JSON,
  setTimeout,
  clearTimeout,
}};
context.window = context;
context.globalThis = context;

async function flushAsync() {{
  for (let index = 0; index < 4; index += 1) {{
    await Promise.resolve();
  }}
  await new Promise((resolve) => setTimeout(resolve, 0));
}}

async function main() {{
  vm.createContext(context);
  vm.runInContext(
    source + "\\n;globalThis.__testExports = {{ renderEntertainment, handleCanaryTaskAction, els }};",
    context,
  );
  await flushAsync();

  const {{ renderEntertainment, handleCanaryTaskAction, els }} = context.__testExports;

  renderEntertainment({{
    interpretation: {{
      entertainment: {{
        persona_lines: [],
        learning_cards: [],
        share_report: reportPayload,
      }},
    }},
  }});
  await flushAsync();

  if (triggerCopyAction && typeof els[triggerCopyAction]?.listeners?.click === "function") {{
    await els[triggerCopyAction].listeners.click();
    await flushAsync();
  }}

  if (triggerCanaryAction) {{
    handleCanaryTaskAction(triggerCanaryAction);
    await flushAsync();
  }}

  process.stdout.write(JSON.stringify({{
    shareReportHtml: elements.shareReport.innerHTML,
    shareReportCardsHtml: elements.shareReportCards.innerHTML,
    shareReportMetaHtml: elements.shareReportMeta.innerHTML,
    shareReportLeadHtml: elements.shareReportLead.innerHTML,
    copyStatusText: elements.shareReportCopyStatus.textContent,
    textCopyDisabled: elements.copyShareReportTextBtn.disabled,
    htmlCopyDisabled: elements.copyShareReportHtmlBtn.disabled,
    draftCopyDisabled: elements.copyShareReportDraftBtn.disabled,
    draftOpen: elements.shareReportDraftDetails.open,
    draftHidden: elements.shareReportDraftDetails.classList.contains("hidden"),
    draftMetaHtml: elements.shareReportDraftMeta.innerHTML,
    draftCardsHtml: elements.shareReportDraftCards.innerHTML,
    clipboardWrites,
    experimentsOpen: elements.experimentsPanel.open,
    shareReportScrollOptions: elements.shareReport.scrollOptions || null,
    textCopyFocused: !!elements.copyShareReportTextBtn.focused,
  }}));
}}

main().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
        return run_realtime_harness(harness)

    def run_learning_path_harness(
        self,
        path_payload: dict,
        cards_payload: dict | None,
        path_status_code: int = 200,
        click_node_id: str | None = None,
        trigger_recommended_node_id: str | None = None,
        trigger_detail_action: str = "mark-read",
        trigger_detail_action_node_id: str | None = None,
        trigger_detail_action_disabled: bool = False,
        progress_status_code: int = 200,
        progress_payload: dict | None = None,
    ) -> dict:
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(APP_JS))}, "utf8");
const pathPayload = {json.dumps(path_payload)};
const cardsPayload = {json.dumps(cards_payload)};
const pathStatusCode = {json.dumps(path_status_code)};
const clickNodeId = {json.dumps(click_node_id)};
const triggerRecommendedNodeId = {json.dumps(trigger_recommended_node_id)};
const triggerDetailAction = {json.dumps(trigger_detail_action)};
const triggerDetailActionNodeId = {json.dumps(trigger_detail_action_node_id)};
const triggerDetailActionDisabled = {json.dumps(trigger_detail_action_disabled)};
const progressStatusCode = {json.dumps(progress_status_code)};
const progressPayload = {json.dumps(progress_payload or {"stored": False, "blocked_reasons": ["productization_not_active"]})};

function createClassList(initial = []) {{
  const set = new Set(initial);
  return {{
    add(name) {{
      set.add(name);
    }},
    remove(name) {{
      set.delete(name);
    }},
    toggle(name, force) {{
      if (force === undefined) {{
        if (set.has(name)) {{
          set.delete(name);
          return false;
        }}
        set.add(name);
        return true;
      }}
      if (force) {{
        set.add(name);
      }} else {{
        set.delete(name);
      }}
      return !!force;
    }},
    contains(name) {{
      return set.has(name);
    }},
    toArray() {{
      return Array.from(set).sort();
    }},
  }};
}}

function createElement(id, tagName = "div") {{
  return {{
    id,
    tagName: tagName.toUpperCase(),
    innerHTML: "",
    textContent: "",
    value: "",
    disabled: false,
    open: false,
    dataset: {{}},
    attributes: {{}},
    classList: createClassList(),
    listeners: {{}},
    addEventListener(type, handler) {{
      if (!this.listeners[type]) {{
        this.listeners[type] = [];
      }}
      this.listeners[type].push(handler);
    }},
    dispatchEvent(event) {{
      const handlers = this.listeners[event.type] || [];
      const promises = [];
      const dispatchedEvent = {{
        ...event,
        currentTarget: this,
        target: event.target || this,
        defaultPrevented: false,
        preventDefault() {{
          this.defaultPrevented = true;
        }},
      }};
      for (const handler of handlers) {{
        const result = handler(dispatchedEvent);
        if (result && typeof result.then === "function") {{
          promises.push(result);
        }}
      }}
      if (promises.length) {{
        return Promise.all(promises);
      }}
      return !dispatchedEvent.defaultPrevented;
    }},
    setAttribute(name, value) {{
      this.attributes[name] = String(value);
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        this.dataset[key] = String(value);
      }}
    }},
    getAttribute(name) {{
      if (Object.prototype.hasOwnProperty.call(this.attributes, name)) {{
        return this.attributes[name];
      }}
      return null;
    }},
    removeAttribute(name) {{
      delete this.attributes[name];
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        delete this.dataset[key];
      }}
    }},
  }};
}}

const elementIds = [
  "connectBtn",
  "disconnectBtn",
  "interruptBtn",
  "modeSelect",
  "testerId",
  "inviteCode",
  "status",
  "textQuestion",
  "runTextInterpretBtn",
  "textInterpretStatus",
  "betaNotice",
  "opsPauseNotice",
  "publicFeedbackNotice",
  "visitorNickname",
  "saveVisitorProfileBtn",
  "visitorProfileStatus",
  "transcript",
  "toolLog",
  "interpretationPreview",
  "explainResult",
  "debugDetails",
  "debugJson",
  "learningMaterials",
  "personaCards",
  "personaCardsToggle",
  "learningCards",
  "learningPathPanel",
  "learningPathSummary",
  "learningPathRecommended",
  "learningPathNodes",
  "learningPathDetail",
  "learningPathStatus",
  "safetyState",
  "feedbackType",
  "feedbackNote",
  "submitFeedbackBtn",
  "feedbackStatus",
  "canaryTaskList",
  "commercialInterest",
  "commercialInterestStatus",
  "offerCatalogList",
  "monetizationStatus",
  "businessLeadNickname",
  "businessLeadChannel",
  "businessLeadSummary",
  "submitBusinessLeadBtn",
  "businessLeadStatus",
  "membershipTiersList",
  "paymentGateStatus",
  "paymentTierSelect",
  "startSandboxCheckoutBtn",
  "confirmSandboxPaymentBtn",
  "failSandboxPaymentBtn",
  "cancelSandboxOrderBtn",
  "refundSandboxOrderBtn",
  "sandboxOrderStatus",
  "shareReport",
  "shareReportMeta",
  "shareReportLead",
  "shareReportCards",
  "shareReportCopyStatus",
  "copyShareReportTextBtn",
  "copyShareReportHtmlBtn",
  "shareReportDraftDetails",
  "shareReportDraftMeta",
  "shareReportDraftCards",
  "copyShareReportDraftBtn",
  "remoteAudio",
];

const elements = Object.fromEntries(
  elementIds.map((id) => [id, createElement(id, id === "learningPathPanel" ? "details" : "div")]),
);
elements.modeSelect.value = "plain";
elements.feedbackType.value = "helpful";

const fetchCalls = [];
const document = {{
  getElementById(id) {{
    return elements[id] || null;
  }},
  querySelector() {{
    return null;
  }},
  querySelectorAll(selector) {{
    if (selector === ".monetizationInterest") {{
      return [];
    }}
    if (selector === ".app-nav a") {{
      return [];
    }}
    return [];
  }},
}};

const fetchStub = async (url, options = {{}}) => {{
  fetchCalls.push({{ url, options }});
  if (url === "/api/learning/path") {{
    return {{ ok: pathStatusCode >= 200 && pathStatusCode < 300, status: pathStatusCode, json: async () => pathPayload }};
  }}
  if (url === "/api/learning/cards") {{
    if (cardsPayload === null) {{
      return {{ ok: false, status: 503, json: async () => ({{}}), text: async () => "" }};
    }}
    return {{ ok: true, json: async () => cardsPayload }};
  }}
  if (url === "/api/learning/progress") {{
    return {{
      ok: progressStatusCode >= 200 && progressStatusCode < 300,
      status: progressStatusCode,
      json: async () => progressPayload,
    }};
  }}
  return {{ ok: true, json: async () => ({{}}), text: async () => "" }};
}};

const context = {{
  console,
  document,
  window: null,
  fetch: fetchStub,
  navigator: {{ mediaDevices: {{ getUserMedia: async () => ({{ getTracks: () => [] }}) }} }},
  RTCPeerConnection: function RTCPeerConnection() {{
    return {{
      addTrack() {{}},
      createDataChannel() {{ return {{ addEventListener() {{}}, close() {{}}, readyState: "open" }}; }},
      createOffer: async () => ({{ sdp: "stub" }}),
      setLocalDescription: async () => {{}},
      setRemoteDescription: async () => {{}},
      close() {{}},
    }};
  }},
  Intl,
  Date,
  JSON,
  setTimeout,
  clearTimeout,
}};
context.window = context;
context.globalThis = context;

async function flushAsync() {{
  for (let index = 0; index < 4; index += 1) {{
    await Promise.resolve();
  }}
  await new Promise((resolve) => setTimeout(resolve, 0));
}}

async function main() {{
  vm.createContext(context);
  vm.runInContext(source, context);
  await flushAsync();

  if (clickNodeId) {{
    const clickResult = elements.learningPathNodes.dispatchEvent({{
      type: "click",
      target: {{ closest: () => ({{ dataset: {{ nodeId: clickNodeId }} }}) }},
    }});
    if (clickResult && typeof clickResult.then === "function") {{
      await clickResult;
    }}
    await flushAsync();
  }}

  if (triggerRecommendedNodeId) {{
    const clickResult = elements.learningPathRecommended.dispatchEvent({{
      type: "click",
      target: {{
        closest: () => ({{
          dataset: {{ action: "start-learning", nodeId: triggerRecommendedNodeId }},
          disabled: false,
        }}),
      }},
    }});
    if (clickResult && typeof clickResult.then === "function") {{
      await clickResult;
    }}
    await flushAsync();
  }}

  if (triggerDetailActionNodeId) {{
    const clickResult = elements.learningPathDetail.dispatchEvent({{
      type: "click",
      target: {{
        closest: () => ({{
          dataset: {{ action: triggerDetailAction, nodeId: triggerDetailActionNodeId }},
          disabled: triggerDetailActionDisabled,
        }}),
      }},
    }});
    if (clickResult && typeof clickResult.then === "function") {{
      await clickResult;
    }}
    await flushAsync();
  }}
  const progressCalls = fetchCalls
    .filter((call) => call.url === "/api/learning/progress")
    .map((call) => {{
      let body = null;
      try {{
        body = call.options?.body ? JSON.parse(call.options.body) : null;
      }} catch (error) {{
        body = {{ parseError: error.message, raw: call.options?.body || null }};
      }}
      return {{
        method: call.options?.method || "GET",
        body,
      }};
    }});
  const learningRequestUrls = fetchCalls
    .map((call) => call.url)
    .filter((url) => url.startsWith("/api/learning/"));

  process.stdout.write(JSON.stringify({{
    recommendedHtml: elements.learningPathRecommended.innerHTML,
    nodesHtml: elements.learningPathNodes.innerHTML,
    detailHtml: elements.learningPathDetail.innerHTML,
    statusText: elements.learningPathStatus.textContent,
    panelOpen: elements.learningPathPanel.open,
    learningRequestUrls,
    progressCalls,
  }}));
}}

main().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
        return run_realtime_harness(harness)

    def test_static_realtime_page_has_expected_elements(self):
        html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")

        for element_id in [
            "connectBtn",
            "disconnectBtn",
            "interruptBtn",
            "modeSelect",
            "status",
            "transcript",
            "toolLog",
            "interpretationPreview",
            "explainResult",
            "debugDetails",
            "debugJson",
            "learningMaterials",
            "personaCards",
            "personaCardsToggle",
            "learningCards",
            "shareReport",
            "shareReportMeta",
            "shareReportLead",
            "shareReportCards",
            "shareReportCopyStatus",
            "copyShareReportTextBtn",
            "copyShareReportHtmlBtn",
            "shareReportDraftDetails",
            "shareReportDraftMeta",
            "shareReportDraftCards",
            "copyShareReportDraftBtn",
            "betaNotice",
            "testerId",
            "safetyState",
            "feedbackType",
            "feedbackNote",
            "submitFeedbackBtn",
            "feedbackStatus",
            "feedbackPanel",
            "remoteAudio",
            "textQuestion",
            "runTextInterpretBtn",
            "textInterpretStatus",
        ]:
            self.assertIn(f'id="{element_id}"', html)

        self.assertNotIn('id="reportText"', html)
        self.assertNotIn('id="pdfReportDraft"', html)

        for label in ["专业", "白话", "故事", "导师"]:
            self.assertIn(label, html)

        self.assertIn("受限内测", html)
        self.assertIn('class="language-switcher"', html)
        self.assertIn('data-language-option="en"', html)
        self.assertIn("学习资料会在生成解释后显示", html)
        self.assertIn("app.js", html)
        self.assertIn("只用于具体事项占问", html)
        self.assertIn("开始起课", html)
        self.assertIn("styles.css", html)
        self.assertIn("details", html)
        self.assertIn("styles.css?v=clickability-2", html)
        self.assertIn("app.js?v=clickability-2", html)

    def test_static_realtime_page_uses_workbench_layout(self):
        html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "static" / "realtime" / "styles.css").read_text(encoding="utf-8")

        for snippet in [
            'class="app-shell"',
            'class="app-topbar"',
            'class="brand-mark"',
            'class="safety-banner"',
            'class="workbench"',
            'class="primary-column"',
            'class="assistant-rail"',
            'class="secondary-grid"',
            'id="questionPanel"',
            'id="resultPanel"',
            'id="supportPanel"',
            'id="experimentsPanel"',
        ]:
            self.assertIn(snippet, html)

        self.assertLess(html.index('id="questionPanel"'), html.index('id="resultPanel"'))
        self.assertLess(html.index('id="resultPanel"'), html.index('id="supportPanel"'))
        self.assertLess(html.index('id="supportPanel"'), html.index('id="experimentsPanel"'))

        for rule in [
            ".workbench",
            ".primary-column",
            ".assistant-rail",
            ".experiments-drawer",
            ".secondary-grid",
            "@media (max-width: 900px)",
            "focus-visible",
            "prefers-reduced-motion",
        ]:
            self.assertIn(rule, css)

    def test_learning_path_panel_moves_into_support_rail_as_drawer(self):
        html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        structure = parse_html_id_structure(html)
        support_match = re.search(r'<aside\b[^>]*\bid="supportPanel"[^>]*>(?P<body>.*?)</aside>', html, re.S)
        experiments_match = re.search(
            r'<details\b[^>]*\bid="experimentsPanel"[^>]*>(?P<body>.*)</details>\s*<audio',
            html,
            re.S,
        )

        self.assertIn('<details id="learningPathPanel"', html)
        self.assertIn("<summary>学习闯关</summary>", html)
        self.assertIn('href="#learningPathPanel"', html)
        self.assertIn('aria-label="推荐下一步"', html)
        self.assertIsNotNone(support_match)
        self.assertIsNotNone(experiments_match)
        self.assertEqual(structure["learningPathPanel"]["tag"], "details")
        self.assertEqual(structure["learningPathPanel"]["parent_id"], "supportPanel")
        self.assertIn("supportPanel", structure["learningPathPanel"]["ancestor_ids"])
        self.assertNotIn("experimentsPanel", structure["learningPathPanel"]["ancestor_ids"])
        self.assertIn('id="learningPathPanel"', support_match.group("body"))
        self.assertNotIn('id="learningPathPanel"', experiments_match.group("body"))
        self.assertLess(
            support_match.group("body").index('id="learningMaterials"'),
            support_match.group("body").index('id="learningPathPanel"'),
        )
        self.assertLess(
            support_match.group("body").index('id="learningPathPanel"'),
            support_match.group("body").index('id="feedbackPanel"'),
        )

        for element_id in [
            "learningPathSummary",
            "learningPathRecommended",
            "learningPathNodes",
            "learningPathDetail",
            "learningPathStatus",
        ]:
            self.assertIn(f'id="{element_id}"', html)
        self.assertNotIn('id="learningPathList"', html)

    def test_static_realtime_experiments_are_collapsed_by_default(self):
        html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")

        self.assertIn('<details id="experimentsPanel"', html)
        self.assertIn('class="experiments-drawer"', html)
        self.assertIn("<summary>更多 / 实验功能</summary>", html)
        self.assertNotIn('<details id="experimentsPanel" open', html)

        experiments_start = html.index('id="experimentsPanel"')
        for element_id in [
            "monetizationPanel",
            "businessLeadPanel",
            "membershipTiersPanel",
            "sandboxPaymentPanel",
            "debugDetails",
            "shareReport",
        ]:
            self.assertIn(f'id="{element_id}"', html)
            self.assertGreater(html.index(f'id="{element_id}"'), experiments_start)

    def test_question_nav_scrolls_and_marks_current(self):
        result = self.run_nav_click_harness("#questionPanel")

        self.assertTrue(result["hasClickHandler"])
        self.assertTrue(result["preventedDefault"])
        self.assertEqual(result["linkCurrentHref"], "#questionPanel")
        self.assertEqual(result["questionPanelScrollOptions"]["block"], "start")
        self.assertEqual(result["questionActiveState"], "true")
        self.assertIn("nav-target-active", result["questionActiveClass"])
        self.assertNotEqual(result["learningPathActiveState"], "true")
        self.assertNotEqual(result["feedbackActiveState"], "true")
        self.assertNotEqual(result["experimentsActiveState"], "true")

    def test_learning_path_nav_opens_details_and_scrolls(self):
        result = self.run_nav_click_harness("#learningPathPanel")

        self.assertTrue(result["hasClickHandler"])
        self.assertTrue(result["preventedDefault"])
        self.assertEqual(result["linkCurrentHref"], "#learningPathPanel")
        self.assertTrue(result["learningPathOpen"])
        self.assertEqual(result["learningPathScrollOptions"]["block"], "start")

    def test_more_nav_keeps_opening_details_and_scrolls(self):
        result = self.run_nav_click_harness("#experimentsPanel")

        self.assertTrue(result["hasClickHandler"])
        self.assertTrue(result["preventedDefault"])
        self.assertTrue(result["experimentsOpen"])
        self.assertEqual(result["experimentsScrollOptions"]["block"], "start")

    def test_feedback_nav_targets_feedback_panel_not_support_aside(self):
        result = self.run_nav_click_harness("#feedbackPanel")

        self.assertTrue(result["hasClickHandler"])
        self.assertTrue(result["preventedDefault"])
        self.assertIsNone(result["supportPanelScrollOptions"])
        self.assertEqual(result["feedbackPanelScrollOptions"]["block"], "start")

    def test_nav_click_updates_aria_current_and_target_activation_hook(self):
        result = self.run_nav_click_harness("#learningPathPanel")

        self.assertEqual(result["linkCurrentHref"], "#learningPathPanel")
        self.assertNotEqual(result["questionActiveState"], "true")
        self.assertEqual(result["learningPathActiveState"], "true")
        self.assertIn("nav-target-active", result["learningPathActiveClass"])

    def test_persona_cards_toggle_has_style_hook(self):
        import re

        html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "static" / "realtime" / "styles.css").read_text(encoding="utf-8")

        button_match = re.search(
            r'<button\b[^>]*\bid="personaCardsToggle"[^>]*>',
            html,
            re.S,
        )
        self.assertIsNotNone(button_match, "personaCardsToggle button tag not found")

        button_tag = button_match.group(0)
        class_match = re.search(r'\bclass="([^"]*)"', button_tag)
        self.assertIsNotNone(class_match, "personaCardsToggle button is missing a class attribute")
        class_tokens = set(class_match.group(1).split())
        self.assertIn("persona-toggle", class_tokens)
        self.assertIn("hidden", class_tokens)

        rule_match = re.search(r"\.persona-toggle\s*\{([^}]*)\}", css, re.S)
        self.assertIsNotNone(rule_match, ".persona-toggle rule block not found")
        rule_block = rule_match.group(1)
        self.assertIn("display: inline-flex", rule_block)
        self.assertIn("margin-top: 12px", rule_block)

    def test_share_report_markup_uses_cards_and_collapsible_draft(self):
        html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="shareReportCards"', html)
        self.assertIn('id="copyShareReportTextBtn"', html)
        self.assertIn('id="copyShareReportHtmlBtn"', html)
        self.assertIn('id="shareReportDraftDetails"', html)
        self.assertIn("<summary>高级草稿</summary>", html)
        self.assertIn('id="copyShareReportDraftBtn"', html)
        self.assertNotIn("<textarea id=\"reportText\"", html)
        self.assertNotIn("<pre id=\"pdfReportDraft\"", html)

    def test_realtime_client_has_core_webrtc_flow_contract(self):
        js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        for snippet in [
            "new RTCPeerConnection",
            "navigator.mediaDevices.getUserMedia",
            'createDataChannel("oai-events")',
            'fetch("/api/realtime/session"',
            'fetch("/api/liuren/interpret"',
            'fetch("/api/liuren/text-interpret"',
            "runTextInterpret",
            "text_interpreting",
            "deepseek",
            "renderReadableResult",
            "renderQuestionFocus",
            "renderNonLiurenQuestion",
            "non_liuren_question",
            "function_call_output",
            "response.create",
            "response.cancel",
            "response.done",
            "renderEntertainment",
            "hasLearningMaterials",
            "els.learningMaterials.open = hasLearningMaterials",
            "renderShareReport",
            "renderBetaStatus",
            "submitFeedback",
            "friendlyBlockedReason",
            "偏好保存暂未开放",
            'fetch("/api/beta/config"',
            'fetch("/api/beta/feedback"',
            'fetch("/api/beta/report"',
            "story",
            "mentor",
        ]:
            self.assertIn(snippet, js)

        self.assertNotIn("访客偏好未记录：", js)
        self.assertNotIn("loadReferenceData();", js)

        for state in ["connecting", "listening", "tool_calling", "responding", "error"]:
            self.assertIn(state, js)

    def test_persona_cards_toggle_contract(self):
        js = (ROOT / "static" / "realtime" / "app.js").read_text(encoding="utf-8")

        for snippet in [
            "personaCardsToggle",
            "personaCardsExpanded",
            "personaCardLines",
            "defaultPersonaCardCount",
            ".slice(0, defaultPersonaCardCount)",
            'classList.toggle("hidden", personaLines.length <= defaultPersonaCardCount)',
            'state.personaCardsExpanded ? "收起" : "展开全部"',
            'personaCardsToggle.addEventListener("click"',
            "state.personaCardsExpanded = !state.personaCardsExpanded",
            "renderPersonaLines(state.personaCardLines)",
            "state.personaCardsExpanded = false;",
        ]:
            self.assertIn(snippet, js)

    def test_persona_cards_toggle_behavior(self):
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(APP_JS))}, "utf8");

function createClassList(initial = []) {{
  const set = new Set(initial);
  return {{
    add(name) {{
      set.add(name);
    }},
    remove(name) {{
      set.delete(name);
    }},
    toggle(name, force) {{
      if (force === undefined) {{
        if (set.has(name)) {{
          set.delete(name);
          return false;
        }}
        set.add(name);
        return true;
      }}
      if (force) {{
        set.add(name);
      }} else {{
        set.delete(name);
      }}
      return !!force;
    }},
    contains(name) {{
      return set.has(name);
    }},
    toArray() {{
      return Array.from(set).sort();
    }},
  }};
}}

function createElement(id) {{
  return {{
    id,
    innerHTML: "",
    textContent: "",
    value: "",
    disabled: false,
    open: false,
    dataset: {{}},
    classList: createClassList(id === "personaCardsToggle" ? ["hidden"] : []),
    listeners: {{}},
    addEventListener(type, handler) {{
      this.listeners[type] = handler;
    }},
  }};
}}

const elementIds = [
  "connectBtn",
  "disconnectBtn",
  "interruptBtn",
  "modeSelect",
  "testerId",
  "inviteCode",
  "status",
  "textQuestion",
  "runTextInterpretBtn",
  "textInterpretStatus",
  "betaNotice",
  "opsPauseNotice",
  "publicFeedbackNotice",
  "visitorNickname",
  "saveVisitorProfileBtn",
  "visitorProfileStatus",
  "transcript",
  "toolLog",
  "interpretationPreview",
  "explainResult",
  "debugDetails",
  "debugJson",
  "learningMaterials",
  "personaCards",
  "personaCardsToggle",
  "learningCards",
  "safetyState",
  "feedbackType",
  "feedbackNote",
  "submitFeedbackBtn",
  "feedbackStatus",
  "canaryTaskList",
  "commercialInterest",
  "commercialInterestStatus",
  "offerCatalogList",
  "monetizationStatus",
  "businessLeadNickname",
  "businessLeadChannel",
  "businessLeadSummary",
  "submitBusinessLeadBtn",
  "businessLeadStatus",
  "membershipTiersList",
  "paymentGateStatus",
  "paymentTierSelect",
  "startSandboxCheckoutBtn",
  "confirmSandboxPaymentBtn",
  "failSandboxPaymentBtn",
  "cancelSandboxOrderBtn",
  "refundSandboxOrderBtn",
  "sandboxOrderStatus",
  "shareReport",
  "reportText",
  "pdfReportDraft",
  "remoteAudio",
];

const elements = Object.fromEntries(elementIds.map((id) => [id, createElement(id)]));
elements.modeSelect.value = "plain";
elements.feedbackType.value = "general";

const monetizationButtons = [];

const document = {{
  getElementById(id) {{
    return elements[id] || null;
  }},
  querySelectorAll(selector) {{
    if (selector === ".monetizationInterest") {{
      return monetizationButtons;
    }}
    return [];
  }},
}};

const fetchStub = async () => ({{ ok: true, json: async () => ({{}}), text: async () => "" }});

const context = {{
  console,
  document,
  window: null,
  fetch: fetchStub,
  navigator: {{ mediaDevices: {{ getUserMedia: async () => ({{ getTracks: () => [] }}) }} }},
  RTCPeerConnection: function RTCPeerConnection() {{
    return {{
      addTrack() {{}},
      createDataChannel() {{ return {{ addEventListener() {{}}, close() {{}}, readyState: "open" }}; }},
      createOffer: async () => ({{ sdp: "stub" }}),
      setLocalDescription: async () => {{}},
      setRemoteDescription: async () => {{}},
      close() {{}},
    }};
  }},
  Intl,
  Date,
  JSON,
  setTimeout,
  clearTimeout,
}};
context.window = context;
context.globalThis = context;

vm.createContext(context);
vm.runInContext(
  source + "\\n;globalThis.__testExports = {{ renderEntertainment, renderPersonaLines, state, els }};",
  context,
);

const {{ renderEntertainment, els }} = context.__testExports;

function personaLines(count, prefix) {{
  const generalNames = ["贵人", "螣蛇", "朱雀", "六合", "勾陈", "青龙", "天空", "白虎", "太常", "玄武", "太阴", "天后"];
  return Array.from({{ length: count }}, (_, index) => ({{
    general: generalNames[index % generalNames.length],
    role_name: `角色${{index + 1}}`,
    line: `${{prefix}}内容${{index + 1}}`,
    safety_note: `提示${{index + 1}}`,
  }}));
}}

function snapshot(label) {{
  return {{
    label,
    renderedCount: (els.personaCards.innerHTML.match(/<section class="persona-card /g) || []).length,
    expandedClass: els.personaCards.classList.contains("persona-cards--expanded"),
    toggleHidden: els.personaCardsToggle.classList.contains("hidden"),
    toggleText: els.personaCardsToggle.textContent,
    html: els.personaCards.innerHTML,
  }};
}}

renderEntertainment({{
  interpretation: {{
    entertainment: {{
      persona_lines: personaLines(6, "甲"),
      learning_cards: [],
      share_report: {{}},
    }},
  }},
}});
const initial = snapshot("initial");

els.personaCardsToggle.listeners.click();
const expanded = snapshot("expanded");

els.personaCardsToggle.listeners.click();
const collapsed = snapshot("collapsed");

renderEntertainment({{
  interpretation: {{
    entertainment: {{
      persona_lines: personaLines(4, "乙"),
      learning_cards: [],
      share_report: {{}},
    }},
  }},
}});
const fourItems = snapshot("fourItems");

renderEntertainment({{
  interpretation: {{
    entertainment: {{
      persona_lines: personaLines(6, "丙"),
      learning_cards: [],
      share_report: {{}},
    }},
  }},
}});
els.personaCardsToggle.listeners.click();
const secondExpanded = snapshot("secondExpanded");

renderEntertainment({{
  interpretation: {{
    entertainment: {{
      persona_lines: personaLines(5, "丁"),
      learning_cards: [],
      share_report: {{}},
    }},
  }},
}});
const resetAfterNewResult = snapshot("resetAfterNewResult");

renderEntertainment({{
  interpretation: {{
    entertainment: {{
      persona_lines: [],
      learning_cards: [],
      share_report: {{}},
    }},
  }},
}});
const emptyState = snapshot("emptyState");

process.stdout.write(JSON.stringify({{
  initial,
  expanded,
  collapsed,
  fourItems,
  secondExpanded,
  resetAfterNewResult,
  emptyState,
}}));
"""

        result = run_realtime_harness(harness)

        self.assertEqual(result["initial"]["renderedCount"], 4)
        self.assertFalse(result["initial"]["expandedClass"])
        self.assertFalse(result["initial"]["toggleHidden"])
        self.assertEqual(result["initial"]["toggleText"], "展开全部")
        self.assertIn("persona-card__content", result["initial"]["html"])
        self.assertIn("/static/realtime/assets/persona-bg/general-guiren@2x.webp", result["initial"]["html"])

        self.assertEqual(result["expanded"]["renderedCount"], 6)
        self.assertTrue(result["expanded"]["expandedClass"])
        self.assertEqual(result["expanded"]["toggleText"], "收起")

        self.assertEqual(result["collapsed"]["renderedCount"], 4)
        self.assertFalse(result["collapsed"]["expandedClass"])
        self.assertEqual(result["collapsed"]["toggleText"], "展开全部")

        self.assertEqual(result["fourItems"]["renderedCount"], 4)
        self.assertFalse(result["fourItems"]["expandedClass"])
        self.assertTrue(result["fourItems"]["toggleHidden"])

        self.assertEqual(result["secondExpanded"]["renderedCount"], 6)
        self.assertTrue(result["secondExpanded"]["expandedClass"])
        self.assertEqual(result["resetAfterNewResult"]["renderedCount"], 4)
        self.assertFalse(result["resetAfterNewResult"]["expandedClass"])
        self.assertEqual(result["resetAfterNewResult"]["toggleText"], "展开全部")
        self.assertFalse(result["resetAfterNewResult"]["toggleHidden"])

        self.assertEqual(result["emptyState"]["renderedCount"], 0)
        self.assertFalse(result["emptyState"]["expandedClass"])
        self.assertIn("本次暂无角色化输出", result["emptyState"]["html"])
        self.assertTrue(result["emptyState"]["toggleHidden"])

    def test_share_report_renders_cards_copy_actions_and_draft_from_legacy_payload(self):
        result = self.run_share_report_harness(
            {
                "report_type": "local_share_report",
                "chart_id": "chart-123",
                "mode": "story",
                "storage": "local_only",
                "text": "\n".join(
                    [
                        "本地分享报告",
                        "报告类型：传统文化学习与娱乐体验",
                        "课题 ID：chart-123",
                        "课体：涉害",
                        "摘要：先稳住节奏，再看合作推进。",
                        "安全提示：仅供传统文化学习与娱乐体验，不构成现实建议。",
                        "故事场景：先对齐边界，再推进合作。",
                        "贵人：先确认彼此底线。",
                    ]
                ),
                "html": "<article data-chart-id='chart-123'><p>local report</p></article>",
                "pdf_report_draft": {
                    "format": "pdf_draft",
                    "title": "RenYu local PDF report draft",
                    "storage": "local_only",
                    "disclaimer": "traditional culture learning and entertainment experience, not real-world advice",
                    "sections": [
                        {"title": "Overview", "content": "先稳住节奏，再看合作推进。"},
                        {"title": "Evidence", "content": "{\"rule\": \"涉害\"}"},
                    ],
                },
            },
            trigger_copy_action="copyShareReportTextBtn",
        )

        self.assertIn("先稳住节奏，再看合作推进。", result["shareReportCardsHtml"])
        self.assertIn("安全提示", result["shareReportCardsHtml"])
        self.assertIn("故事场景", result["shareReportCardsHtml"])
        self.assertIn("chart-123", result["shareReportMetaHtml"])
        self.assertFalse(result["textCopyDisabled"])
        self.assertFalse(result["htmlCopyDisabled"])
        self.assertFalse(result["draftCopyDisabled"])
        self.assertFalse(result["draftHidden"])
        self.assertIn("文档草稿", result["draftMetaHtml"])
        self.assertIn("概览", result["draftCardsHtml"])
        self.assertNotIn("pdf_draft", result["draftMetaHtml"])
        self.assertNotIn("Overview", result["draftCardsHtml"])
        self.assertEqual(len(result["clipboardWrites"]), 1)
        self.assertIn("本地分享报告", result["clipboardWrites"][0])
        self.assertIn("已复制", result["copyStatusText"])

    def test_share_report_renders_structured_object_and_list_sections_readably(self):
        result = self.run_share_report_harness(
            {
                "report_type": "local_share_report",
                "chart_id": "chart-structured",
                "sections": [
                    {
                        "title": "起课事实",
                        "kind": "object",
                        "content": {
                            "question": "合作推进是否适合继续？",
                            "chart_id": "chart-structured",
                            "lesson_type": "涉害",
                            "category": "合作",
                            "datetime": "2026-05-11T10:00:00+08:00",
                            "evidence_count": 3,
                            "evidence": [{"rule": "raw evidence should stay out"}],
                        },
                    },
                    {
                        "title": "学习节点",
                        "kind": "list",
                        "items": [
                            {"title": "先看四课", "general": "贵人", "line": "确认边界"},
                            {"node_id": "N-2", "status": "todo", "summary": "整理三传顺序"},
                        ],
                    },
                ],
                "draft": {
                    "sections": [
                        {
                            "title": "模型草稿",
                            "content": '{"debug": {"raw": true}, "long": "' + ("x" * 180) + '"}',
                        }
                    ]
                },
            }
        )

        self.assertIn("合作推进是否适合继续？", result["shareReportCardsHtml"])
        self.assertIn("课体：涉害", result["shareReportCardsHtml"])
        self.assertIn("证据数：3", result["shareReportCardsHtml"])
        self.assertIn("先看四课", result["shareReportCardsHtml"])
        self.assertIn("贵人 - 确认边界", result["shareReportCardsHtml"])
        self.assertIn("N-2 / 待处理", result["shareReportCardsHtml"])
        self.assertNotIn("[object Object]", result["shareReportCardsHtml"])
        self.assertNotIn("raw evidence should stay out", result["shareReportCardsHtml"])
        self.assertIn("share-report-card--technical", result["draftCardsHtml"])

    def test_share_report_css_constrains_cards_and_technical_drafts(self):
        css = (ROOT / "static" / "realtime" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("align-items: start", css)
        self.assertIn("min-width: 0", css)
        self.assertIn("overflow-wrap: anywhere", css)
        self.assertIn(".share-report-card--technical", css)
        self.assertIn("max-height:", css)
        self.assertIn("overflow: auto", css)
        self.assertIn("white-space: pre-wrap", css)

    def test_focus_share_report_opens_experiments_drawer_before_scrolling(self):
        result = self.run_share_report_harness(
            {
                "report_type": "local_share_report",
                "chart_id": "chart-123",
                "mode": "plain",
                "storage": "local_only",
                "text": "本地分享报告\n摘要：适合整理给自己看。",
                "html": "<article><p>report</p></article>",
            },
            trigger_canary_action="focus_share_report",
        )

        self.assertTrue(result["experimentsOpen"])
        self.assertEqual(result["shareReportScrollOptions"]["block"], "start")
        self.assertTrue(result["textCopyFocused"])

    def test_chinese_share_report_hides_known_backend_english_labels(self):
        result = self.run_share_report_harness(
            {
                "report_type": "local_share_report",
                "chart_id": "chart-localized",
                "mode": "plain",
                "storage": "local_only",
                "title": "RenYu local share report",
                "summary": "本次报告只在本地整理。",
                "sections": [
                    {"title": "Overview", "content": "先稳住节奏，再看合作推进。"},
                    {
                        "title": "Chart Facts",
                        "kind": "object",
                        "content": {"lesson_type": "涉害", "status": "todo"},
                    },
                    {"title": "Persona Lines", "items": [{"title": "贵人", "status": "completed"}]},
                    {"title": "Learning Cards", "items": [{"title": "先看四课", "status": "started"}]},
                    {"title": "Safety", "content": "仅供传统文化学习与娱乐体验。"},
                ],
            }
        )

        visible_html = "\n".join(
            [
                result["shareReportLeadHtml"],
                result["shareReportMetaHtml"],
                result["shareReportCardsHtml"],
            ]
        )
        self.assertIn("澹语本地分享报告", visible_html)
        self.assertIn("本地分享报告", visible_html)
        self.assertIn("课式信息", visible_html)
        self.assertIn("角色化句子", visible_html)
        self.assertIn("学习卡", visible_html)
        self.assertIn("仅本地", visible_html)
        self.assertIn("白话", visible_html)
        self.assertIn("待处理", visible_html)
        self.assertNotIn("RenYu local share report", visible_html)
        self.assertNotIn("Overview", visible_html)
        self.assertNotIn("Chart Facts", visible_html)
        self.assertNotIn("Persona Lines", visible_html)
        self.assertNotIn("Learning Cards", visible_html)
        self.assertNotIn("Safety", visible_html)
        self.assertNotIn("local_share_report", visible_html)
        self.assertNotIn("local_only", visible_html)
        self.assertNotIn("plain", visible_html)

    def test_browser_client_passes_node_syntax_check(self):
        app_js = ROOT / "static" / "realtime" / "app.js"
        result = subprocess.run(
            ["node", "--check", str(app_js)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"node --check failed for {app_js}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_persona_background_assets_exist(self):
        asset_dir = ROOT / "static" / "realtime" / "assets" / "persona-bg"
        expected = [
            "general-baihu@2x.webp",
            "general-gouchen@2x.webp",
            "general-guiren@2x.webp",
            "general-liuhe@2x.webp",
            "general-qinglong@2x.webp",
            "general-taichang@2x.webp",
            "general-taiyin@2x.webp",
            "general-tengshe@2x.webp",
            "general-tianhou@2x.webp",
            "general-tiankong@2x.webp",
            "general-xuanwu@2x.webp",
            "general-zhuque@2x.webp",
        ]
        self.assertTrue(asset_dir.exists())
        self.assertEqual(sorted(path.name for path in asset_dir.glob("*.webp")), expected)

    def test_learning_path_recommends_first_approved_node_and_renders_buttons(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {
                        "node_id": "LP-R0",
                        "topic": "nine_rules",
                        "title": "Research Primer",
                        "learning_card_ids": ["LC-099"],
                        "source_ids": ["RC-060"],
                        "example_case_ids": ["GC-099"],
                        "review_status": "research_only",
                        "unlocked_outputs": ["research_note"],
                    },
                    {
                        "node_id": "LP-A",
                        "topic": "four_lessons",
                        "title": "Four lessons",
                        "learning_card_ids": ["LC-001"],
                        "source_ids": ["RC-013"],
                        "example_case_ids": ["GC-001"],
                        "review_status": "approved_for_mvp",
                        "unlocked_outputs": ["learning_note"],
                    },
                    {
                        "node_id": "LP-C",
                        "topic": "generals",
                        "title": "Heavenly Generals",
                        "learning_card_ids": ["LC-004"],
                        "source_ids": ["RC-015"],
                        "example_case_ids": ["GC-061"],
                        "review_status": "research_only",
                        "unlocked_outputs": ["reflection_note"],
                    },
                ]
            },
            cards_payload={
                "learning_cards": [
                    {
                        "card_id": "LC-099",
                        "title": "研究先导",
                        "summary": "仅供研究浏览。",
                        "tags": ["研究"],
                        "source_ids": ["RC-060"],
                    },
                    {
                        "card_id": "LC-001",
                        "title": "四课结构",
                        "summary": "看四课骨架。",
                        "tags": ["四课"],
                        "source_ids": ["RC-013"],
                    },
                    {
                        "card_id": "LC-004",
                        "title": "天将角色",
                        "summary": "角色化理解天将。",
                        "tags": ["天将"],
                        "source_ids": ["RC-015"],
                    },
                ]
            },
            trigger_recommended_node_id="LP-A",
        )

        self.assertIn("/api/learning/path", result["learningRequestUrls"])
        self.assertIn("/api/learning/cards", result["learningRequestUrls"])
        self.assertIn("推荐下一步", result["recommendedHtml"])
        self.assertIn("Four lessons", result["recommendedHtml"])
        self.assertNotIn("Research Primer", result["recommendedHtml"])
        self.assertIn("先看四课结构", result["recommendedHtml"])
        self.assertIn("Research Primer", result["nodesHtml"])
        self.assertIn("Heavenly Generals", result["nodesHtml"])
        self.assertIn("1 张学习卡", result["nodesHtml"])
        self.assertEqual(len(result["progressCalls"]), 1)
        self.assertEqual(result["progressCalls"][0]["method"], "POST")
        self.assertEqual(result["progressCalls"][0]["body"]["node_id"], "LP-A")
        self.assertEqual(result["progressCalls"][0]["body"]["status"], "started")
        self.assertEqual(result["progressCalls"][0]["body"]["event_type"], "learning_progress")
        self.assertEqual(result["progressCalls"][0]["body"]["source"], "realtime_frontend")
        self.assertIn("Four lessons", result["detailHtml"])
        self.assertIn("当前不保存进度，不影响浏览。", result["statusText"])

    def test_learning_path_clicking_node_updates_detail(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {
                        "node_id": "LP-A",
                        "topic": "four_lessons",
                        "title": "Four lessons",
                        "learning_card_ids": ["LC-001"],
                        "source_ids": ["RC-013", "RC-014"],
                        "example_case_ids": ["GC-001"],
                        "review_status": "approved_for_mvp",
                        "unlocked_outputs": ["learning_note", "practice_prompt"],
                    },
                ]
            },
            cards_payload={
                "learning_cards": [
                    {
                        "card_id": "LC-001",
                        "title": "四课结构",
                        "summary": "看四课骨架。",
                        "tags": ["四课"],
                        "source_ids": ["RC-013"],
                    },
                ]
            },
            click_node_id="LP-A",
        )

        self.assertIn("/api/learning/path", result["learningRequestUrls"])
        self.assertIn("/api/learning/cards", result["learningRequestUrls"])
        self.assertIn("Four lessons", result["detailHtml"])
        self.assertIn("可学", result["detailHtml"])
        self.assertIn("RC-013", result["detailHtml"])
        self.assertIn("RC-014", result["detailHtml"])
        self.assertIn("learning_note", result["detailHtml"])
        self.assertIn("practice_prompt", result["detailHtml"])
        self.assertIn("先看四课结构", result["detailHtml"])
        self.assertIn("查看学习卡", result["detailHtml"])
        self.assertIn("四课结构", result["detailHtml"])
        self.assertIn("看四课骨架。", result["detailHtml"])
        self.assertEqual(result["progressCalls"], [])

    def test_learning_path_research_only_node_shows_read_only_state(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {
                        "node_id": "LP-B",
                        "topic": "nine_rules",
                        "title": "Nine methods",
                        "learning_card_ids": ["LC-003"],
                        "source_ids": ["RC-060"],
                        "example_case_ids": ["GC-060"],
                        "review_status": "research_only",
                        "unlocked_outputs": ["research_note"],
                    },
                ]
            },
            cards_payload={
                "learning_cards": [
                    {
                        "card_id": "LC-003",
                        "title": "九宗门",
                        "summary": "研究性内容。",
                        "tags": ["三传"],
                        "source_ids": ["RC-060"],
                    },
                ]
            },
            click_node_id="LP-B",
            trigger_detail_action_node_id="LP-B",
            trigger_detail_action_disabled=True,
        )

        self.assertIn("/api/learning/path", result["learningRequestUrls"])
        self.assertIn("/api/learning/cards", result["learningRequestUrls"])
        self.assertIn("Nine methods", result["detailHtml"])
        self.assertIn("研究中", result["detailHtml"])
        self.assertIn("RC-060", result["detailHtml"])
        self.assertIn("research_note", result["detailHtml"])
        self.assertIn("当前仅供研究参考，暂不写入学习进度。", result["detailHtml"])
        self.assertIn("当前暂无可学节点", result["recommendedHtml"])
        self.assertIn("九宗门", result["detailHtml"])
        self.assertIn("研究性内容。", result["detailHtml"])
        self.assertEqual(result["progressCalls"], [])

    def test_learning_path_cards_failure_keeps_nodes_and_shows_degraded_detail(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {
                        "node_id": "LP-A",
                        "topic": "four_lessons",
                        "title": "Four lessons",
                        "learning_card_ids": ["LC-001"],
                        "source_ids": ["RC-013"],
                        "example_case_ids": ["GC-001"],
                        "review_status": "approved_for_mvp",
                        "unlocked_outputs": ["learning_note"],
                    },
                ]
            },
            cards_payload=None,
            click_node_id="LP-A",
        )

        self.assertIn("/api/learning/path", result["learningRequestUrls"])
        self.assertIn("/api/learning/cards", result["learningRequestUrls"])
        self.assertIn("Four lessons", result["nodesHtml"])
        self.assertIn("关联学习卡暂不可用", result["detailHtml"])
        self.assertEqual(result["progressCalls"], [])

    def test_learning_path_view_cards_status_matches_degraded_state(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {
                        "node_id": "LP-A",
                        "topic": "four_lessons",
                        "title": "Four lessons",
                        "learning_card_ids": ["LC-001"],
                        "source_ids": ["RC-013"],
                        "example_case_ids": ["GC-001"],
                        "review_status": "approved_for_mvp",
                        "unlocked_outputs": ["learning_note"],
                    },
                ]
            },
            cards_payload=None,
            click_node_id="LP-A",
            trigger_detail_action="view-cards",
            trigger_detail_action_node_id="LP-A",
        )

        self.assertIn("关联学习卡暂不可用", result["detailHtml"])
        self.assertEqual(result["statusText"], "关联学习卡暂不可用，请先阅读节点摘要与来源。")
        self.assertEqual(result["progressCalls"], [])

    def test_learning_path_progress_http_failure_surfaces_error_state(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {
                        "node_id": "LP-A",
                        "topic": "four_lessons",
                        "title": "Four lessons",
                        "learning_card_ids": ["LC-001"],
                        "source_ids": ["RC-013"],
                        "example_case_ids": ["GC-001"],
                        "review_status": "approved_for_mvp",
                        "unlocked_outputs": ["learning_note"],
                    },
                ]
            },
            cards_payload={
                "learning_cards": [
                    {
                        "card_id": "LC-001",
                        "title": "四课结构",
                        "summary": "看四课骨架。",
                        "tags": ["四课"],
                        "source_ids": ["RC-013"],
                    },
                ]
            },
            trigger_recommended_node_id="LP-A",
            progress_status_code=500,
            progress_payload={"error": "server_error"},
        )

        self.assertEqual(len(result["progressCalls"]), 1)
        self.assertEqual(result["progressCalls"][0]["body"]["node_id"], "LP-A")
        self.assertEqual(result["statusText"], "学习进度记录失败。")

    def test_learning_path_path_failure_uses_consistent_unavailable_state(self):
        result = self.run_learning_path_harness(
            path_payload={"nodes": []},
            cards_payload={"learning_cards": []},
            path_status_code=503,
        )

        self.assertIn("学习闯关暂不可用", result["recommendedHtml"])
        self.assertIn("学习闯关暂不可用", result["nodesHtml"])
        self.assertIn("请稍后重试", result["detailHtml"])
        self.assertEqual(result["statusText"], "学习闯关暂不可用。")
        self.assertEqual(result["progressCalls"], [])

    def run_canary_task_harness(
        self,
        config_payload: dict,
        status_payload: dict,
        task_status_code: int = 200,
    ) -> dict:
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(APP_JS))}, "utf8");
const configPayload = {json.dumps(config_payload)};
const statusPayload = {json.dumps(status_payload)};
const taskStatusCode = {json.dumps(task_status_code)};

function createClassList(initial = []) {{
  const set = new Set(initial);
  return {{
    add(name) {{ set.add(name); }},
    remove(name) {{ set.delete(name); }},
    toggle(name, force) {{
      if (force === undefined) {{
        if (set.has(name)) {{
          set.delete(name);
          return false;
        }}
        set.add(name);
        return true;
      }}
      if (force) {{
        set.add(name);
      }} else {{
        set.delete(name);
      }}
      return !!force;
    }},
    contains(name) {{ return set.has(name); }},
  }};
}}

function createElement(id, tagName = "div") {{
  return {{
    id,
    tagName: tagName.toUpperCase(),
    innerHTML: "",
    textContent: "",
    value: "",
    disabled: false,
    open: false,
    style: {{}},
    dataset: {{}},
    attributes: {{}},
    className: "",
    classList: createClassList(),
    listeners: {{}},
    addEventListener(type, handler) {{
      this.listeners[type] = handler;
    }},
    scrollIntoView(options) {{
      this.scrollOptions = options;
    }},
    setAttribute(name, value) {{
      this.attributes[name] = String(value);
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        this.dataset[key] = String(value);
      }}
    }},
    getAttribute(name) {{
      return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null;
    }},
    removeAttribute(name) {{
      delete this.attributes[name];
    }},
    focus() {{
      this.focused = true;
    }},
  }};
}}

const elementIds = [
  "connectBtn",
  "disconnectBtn",
  "interruptBtn",
  "modeSelect",
  "testerId",
  "inviteCode",
  "status",
  "textQuestion",
  "runTextInterpretBtn",
  "textInterpretStatus",
  "betaNotice",
  "opsPauseNotice",
  "publicFeedbackNotice",
  "visitorNickname",
  "saveVisitorProfileBtn",
  "visitorProfileStatus",
  "transcript",
  "toolLog",
  "interpretationPreview",
  "explainResult",
  "debugDetails",
  "debugJson",
  "learningMaterials",
  "personaCards",
  "personaCardsToggle",
  "learningCards",
  "learningPathPanel",
  "learningPathSummary",
  "learningPathRecommended",
  "learningPathNodes",
  "learningPathDetail",
  "learningPathStatus",
  "safetyState",
  "feedbackType",
  "feedbackNote",
  "submitFeedbackBtn",
  "feedbackStatus",
  "canaryStatusBadge",
  "canaryOverview",
  "canaryProgressLabel",
  "canaryProgressBarFill",
  "canaryMilestones",
  "canaryTaskList",
  "commercialInterest",
  "commercialInterestStatus",
  "offerCatalogList",
  "monetizationStatus",
  "businessLeadNickname",
  "businessLeadChannel",
  "businessLeadSummary",
  "submitBusinessLeadBtn",
  "businessLeadStatus",
  "membershipTiersList",
  "paymentGateStatus",
  "paymentTierSelect",
  "startSandboxCheckoutBtn",
  "confirmSandboxPaymentBtn",
  "failSandboxPaymentBtn",
  "cancelSandboxOrderBtn",
  "refundSandboxOrderBtn",
  "sandboxOrderStatus",
  "shareReport",
  "reportText",
  "pdfReportDraft",
  "remoteAudio",
  "questionPanel",
  "feedbackPanel",
  "experimentsPanel",
];

const elements = Object.fromEntries(
  elementIds.map((id) => [id, createElement(id, id === "experimentsPanel" ? "details" : "div")]),
);
elements.modeSelect.value = "plain";
elements.feedbackType.value = "helpful";

const document = {{
  getElementById(id) {{
    return elements[id] || null;
  }},
  querySelector() {{
    return null;
  }},
  querySelectorAll(selector) {{
    if (selector === ".monetizationInterest" || selector === ".app-nav a") {{
      return [];
    }}
    return [];
  }},
}};

const fetchStub = async (url) => {{
  if (url === "/api/canary/run/config") {{
    return {{ ok: true, status: 200, json: async () => configPayload }};
  }}
  if (url.startsWith("/api/canary/tasks/status")) {{
    return {{
      ok: taskStatusCode >= 200 && taskStatusCode < 300,
      status: taskStatusCode,
      json: async () => statusPayload,
    }};
  }}
  if (url === "/api/beta/config") {{
    return {{ ok: true, status: 200, json: async () => ({{ tester_notice: "Beta notice" }}) }};
  }}
  if (url === "/api/beta/report") {{
    return {{ ok: true, status: 200, json: async () => ({{}}) }};
  }}
  if (url === "/api/ops/status") {{
    return {{ ok: true, status: 200, json: async () => ({{ status: "canary", blocked_reasons: [] }}) }};
  }}
  if (url === "/api/public/status") {{
    return {{ ok: true, status: 200, json: async () => ({{ launch_status: "blocked" }}) }};
  }}
  if (url === "/api/productization/gate") {{
    return {{ ok: true, status: 200, json: async () => ({{ gate_status: "blocked" }}) }};
  }}
  if (url === "/api/monetization/gate") {{
    return {{ ok: true, status: 200, json: async () => ({{ gate_status: "blocked" }}) }};
  }}
  if (url === "/api/payment/gate") {{
    return {{ ok: true, status: 200, json: async () => ({{ gate_status: "blocked" }}) }};
  }}
  if (url === "/api/learning/path") {{
    return {{ ok: true, status: 200, json: async () => ({{ nodes: [] }}) }};
  }}
  if (url === "/api/monetization/offers") {{
    return {{ ok: true, status: 200, json: async () => ({{ offers: [] }}) }};
  }}
  if (url === "/api/membership/tiers") {{
    return {{ ok: true, status: 200, json: async () => ({{ tiers: [] }}) }};
  }}
  if (url === "/api/learning/cards") {{
    return {{ ok: true, status: 200, json: async () => ({{ learning_cards: [] }}) }};
  }}
  return {{ ok: true, status: 200, json: async () => ({{}}), text: async () => "" }};
}};

const context = {{
  console,
  document,
  window: null,
  fetch: fetchStub,
  navigator: {{ mediaDevices: {{ getUserMedia: async () => ({{ getTracks: () => [] }}) }} }},
  RTCPeerConnection: function RTCPeerConnection() {{
    return {{
      addTrack() {{}},
      createDataChannel() {{ return {{ addEventListener() {{}}, close() {{}}, readyState: "open" }}; }},
      createOffer: async () => ({{ sdp: "stub" }}),
      setLocalDescription: async () => {{}},
      setRemoteDescription: async () => {{}},
      close() {{}},
    }};
  }},
  Intl,
  Date,
  JSON,
  setTimeout,
  clearTimeout,
}};
context.window = context;
context.globalThis = context;

async function flushAsync() {{
  for (let index = 0; index < 4; index += 1) {{
    await Promise.resolve();
  }}
  await new Promise((resolve) => setTimeout(resolve, 0));
}}

async function main() {{
  vm.createContext(context);
  vm.runInContext(source, context);
  await flushAsync();

  process.stdout.write(JSON.stringify({{
    badgeText: elements.canaryStatusBadge.textContent,
    badgeClass: elements.canaryStatusBadge.className,
    overviewText: elements.canaryOverview.textContent,
    progressText: elements.canaryProgressLabel.textContent,
    progressWidth: elements.canaryProgressBarFill.style.width || "",
    milestonesHtml: elements.canaryMilestones.innerHTML,
    taskListHtml: elements.canaryTaskList.innerHTML,
  }}));
}}

main().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
        return run_realtime_harness(harness)

    def test_canary_task_panel_renders_progress_cards(self):
        result = self.run_canary_task_harness(
            config_payload={
                "tester_tasks": [
                    {"task_id": "C11-T01", "stage": "必测", "label": "完成一次低风险语音起课", "description": "完成一次实时语音起课。", "cta_label": "去做语音起课", "cta_action": "focus_question"},
                    {"task_id": "C11-T02", "stage": "必测", "label": "切换一次故事或导师口吻", "description": "切换一次 story 或 mentor。", "cta_label": "切到故事口吻", "cta_action": "switch_to_story"},
                ],
            },
            status_payload={
                "overall_status": "in_progress",
                "identity_status": "matched",
                "tester_progress": {"completed_task_count": 1, "total_task_count": 2},
                "ops_status": {"status": "canary", "blocked_reasons": [], "notice": ""},
                "cohort_progress": {
                    "session_count": 8,
                    "feedback_submit_count": 3,
                    "share_report_count": 1,
                    "thresholds": {"min_sessions": 20, "min_feedback_submissions": 10, "min_share_reports": 3},
                },
                "tasks": [
                    {"task_id": "C11-T01", "stage": "必测", "label": "完成一次低风险语音起课", "description": "完成一次实时语音起课。", "cta_label": "去做语音起课", "cta_action": "focus_question", "status": "completed", "completed": True, "completed_at": "2026-05-11T07:00:00Z"},
                    {"task_id": "C11-T02", "stage": "必测", "label": "切换一次故事或导师口吻", "description": "切换一次 story 或 mentor。", "cta_label": "切到故事口吻", "cta_action": "switch_to_story", "status": "todo", "completed": False, "completed_at": ""},
                ],
            },
        )

        self.assertEqual(result["badgeText"], "灰测可继续")
        self.assertIn("is-active", result["badgeClass"])
        self.assertEqual(result["progressText"], "1 / 2 已完成")
        self.assertEqual(result["progressWidth"], "50%")
        self.assertIn("会话 8 / 20", result["milestonesHtml"])
        self.assertIn("完成一次低风险语音起课", result["taskListHtml"])
        self.assertIn("已完成", result["taskListHtml"])
        self.assertIn("切换一次故事或导师口吻", result["taskListHtml"])
        self.assertIn("查看任务", result["taskListHtml"])
        self.assertIn("切到故事口吻", result["taskListHtml"])

    def test_canary_task_panel_falls_back_when_status_unavailable(self):
        result = self.run_canary_task_harness(
            config_payload={"tester_tasks": []},
            status_payload={},
            task_status_code=503,
        )

        self.assertEqual(result["badgeText"], "任务暂不可用")
        self.assertIn("is-blocked", result["badgeClass"])
        self.assertEqual(result["overviewText"], "灰测状态暂不可用，请稍后重试。")
        self.assertIn("灰测状态暂不可用", result["taskListHtml"])

    def run_monetization_console_harness(
        self,
        growth_payload: dict,
        gate_payload: dict,
        metrics_payload: dict,
        offers_payload: dict,
        growth_event_response: dict | None = None,
        monetization_event_response: dict | None = None,
        trigger_growth_click: bool = False,
        trigger_monetization_click: bool = False,
        tester_id: str = "T-001",
    ) -> dict:
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(APP_JS))}, "utf8");
const growthPayload = {json.dumps(growth_payload)};
const gatePayload = {json.dumps(gate_payload)};
const metricsPayload = {json.dumps(metrics_payload)};
const offersPayload = {json.dumps(offers_payload)};
const growthEventResponse = {json.dumps(growth_event_response or {"stored": True, "metrics": growth_payload})};
const monetizationEventResponse = {json.dumps(monetization_event_response or {"stored": False, "blocked_reasons": ["monetization_not_active"], "gate": gate_payload})};
const triggerGrowthClick = {json.dumps(trigger_growth_click)};
const triggerMonetizationClick = {json.dumps(trigger_monetization_click)};
const testerIdValue = {json.dumps(tester_id)};

function createClassList(initial = []) {{
  const set = new Set(initial);
  return {{
    add(name) {{ set.add(name); }},
    remove(name) {{ set.delete(name); }},
    toggle(name, force) {{
      if (force === undefined) {{
        if (set.has(name)) {{
          set.delete(name);
          return false;
        }}
        set.add(name);
        return true;
      }}
      if (force) {{
        set.add(name);
      }} else {{
        set.delete(name);
      }}
      return !!force;
    }},
    contains(name) {{ return set.has(name); }},
  }};
}}

function createElement(id, tagName = "div") {{
  return {{
    id,
    tagName: tagName.toUpperCase(),
    innerHTML: "",
    textContent: "",
    value: "",
    disabled: false,
    open: false,
    style: {{}},
    dataset: {{}},
    attributes: {{}},
    className: "",
    classList: createClassList(),
    listeners: {{}},
    addEventListener(type, handler) {{
      this.listeners[type] = handler;
    }},
    scrollIntoView(options) {{
      this.scrollOptions = options;
    }},
    setAttribute(name, value) {{
      this.attributes[name] = String(value);
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        this.dataset[key] = String(value);
      }}
    }},
    getAttribute(name) {{
      return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null;
    }},
    removeAttribute(name) {{
      delete this.attributes[name];
    }},
    focus() {{
      this.focused = true;
    }},
  }};
}}

const elementIds = [
  "connectBtn",
  "disconnectBtn",
  "interruptBtn",
  "modeSelect",
  "testerId",
  "inviteCode",
  "status",
  "textQuestion",
  "runTextInterpretBtn",
  "textInterpretStatus",
  "betaNotice",
  "opsPauseNotice",
  "publicFeedbackNotice",
  "visitorNickname",
  "saveVisitorProfileBtn",
  "visitorProfileStatus",
  "transcript",
  "toolLog",
  "interpretationPreview",
  "explainResult",
  "debugDetails",
  "debugJson",
  "learningMaterials",
  "personaCards",
  "personaCardsToggle",
  "learningCards",
  "learningPathPanel",
  "learningPathSummary",
  "learningPathRecommended",
  "learningPathNodes",
  "learningPathDetail",
  "learningPathStatus",
  "safetyState",
  "feedbackType",
  "feedbackNote",
  "submitFeedbackBtn",
  "feedbackStatus",
  "canaryStatusBadge",
  "canaryOverview",
  "canaryProgressLabel",
  "canaryProgressBarFill",
  "canaryMilestones",
  "canaryTaskList",
  "commercialInterest",
  "commercialInterestSummary",
  "commercialInterestStatus",
  "monetizationGateBadge",
  "monetizationMetricsHeadline",
  "monetizationOverview",
  "monetizationReasonList",
  "monetizationMetricsList",
  "offerCatalogList",
  "monetizationStatus",
  "businessLeadNickname",
  "businessLeadChannel",
  "businessLeadSummary",
  "submitBusinessLeadBtn",
  "businessLeadStatus",
  "membershipTiersList",
  "paymentGateStatus",
  "paymentTierSelect",
  "startSandboxCheckoutBtn",
  "confirmSandboxPaymentBtn",
  "failSandboxPaymentBtn",
  "cancelSandboxOrderBtn",
  "refundSandboxOrderBtn",
  "sandboxOrderStatus",
  "shareReport",
  "reportText",
  "pdfReportDraft",
  "remoteAudio",
  "questionPanel",
  "feedbackPanel",
  "experimentsPanel",
];

const elements = Object.fromEntries(
  elementIds.map((id) => [id, createElement(id, id === "experimentsPanel" ? "details" : "div")]),
);
elements.modeSelect.value = "plain";
elements.feedbackType.value = "helpful";
elements.testerId.value = testerIdValue;

const monetizationButtons = [
  Object.assign(createElement("monetizationButton0", "button"), {{
    dataset: {{ eventType: "member_interest", offerId: "offer-membership-v0" }},
  }}),
];

const document = {{
  getElementById(id) {{
    return elements[id] || null;
  }},
  querySelector() {{
    return null;
  }},
  querySelectorAll(selector) {{
    if (selector === ".monetizationInterest") {{
      return monetizationButtons;
    }}
    return [];
  }},
}};

const fetchCalls = [];
const fetchStub = async (url, options = {{}}) => {{
  const body = typeof options.body === "string" ? JSON.parse(options.body) : null;
  fetchCalls.push({{ url, method: options.method || "GET", body }});
  if (url === "/api/beta/config") {{
    return {{ ok: true, status: 200, json: async () => ({{ tester_notice: "Beta notice" }}), text: async () => "" }};
  }}
  if (url === "/api/beta/report") {{
    return {{ ok: true, status: 200, json: async () => ({{}}), text: async () => "" }};
  }}
  if (url === "/api/ops/status") {{
    return {{ ok: true, status: 200, json: async () => ({{ status: "canary", blocked_reasons: [] }}), text: async () => "" }};
  }}
  if (url === "/api/public/status") {{
    return {{ ok: true, status: 200, json: async () => ({{ launch_status: "blocked" }}), text: async () => "" }};
  }}
  if (url === "/api/productization/gate") {{
    return {{ ok: true, status: 200, json: async () => ({{ gate_status: "blocked" }}), text: async () => "" }};
  }}
  if (url === "/api/growth/metrics") {{
    return {{ ok: true, status: 200, json: async () => growthPayload, text: async () => "" }};
  }}
  if (url === "/api/growth/event") {{
    return {{ ok: true, status: 200, json: async () => growthEventResponse, text: async () => "" }};
  }}
  if (url === "/api/monetization/gate") {{
    return {{ ok: true, status: 200, json: async () => gatePayload, text: async () => "" }};
  }}
  if (url === "/api/monetization/metrics") {{
    return {{ ok: true, status: 200, json: async () => metricsPayload, text: async () => "" }};
  }}
  if (url === "/api/monetization/offers") {{
    return {{ ok: true, status: 200, json: async () => offersPayload, text: async () => "" }};
  }}
  if (url === "/api/monetization/event") {{
    return {{ ok: true, status: 200, json: async () => monetizationEventResponse, text: async () => "" }};
  }}
  if (url === "/api/business/lead") {{
    return {{ ok: true, status: 200, json: async () => ({{ stored: false, blocked_reasons: ["monetization_not_active"] }}), text: async () => "" }};
  }}
  if (url === "/api/payment/gate") {{
    return {{ ok: true, status: 200, json: async () => ({{ gate_status: "blocked", blocked_reasons: ["insufficient_monetization_interest"] }}), text: async () => "" }};
  }}
  if (url === "/api/payment/metrics") {{
    return {{ ok: true, status: 200, json: async () => ({{ order_count: 0, pending_payment_count: 0, paid_sandbox_count: 0, refunded_count: 0, blocked_order_count: 0 }}), text: async () => "" }};
  }}
  if (url === "/api/canary/run/config") {{
    return {{ ok: true, status: 200, json: async () => ({{ tester_tasks: [] }}), text: async () => "" }};
  }}
  if (url.startsWith("/api/canary/tasks/status")) {{
    return {{ ok: true, status: 200, json: async () => ({{}}), text: async () => "" }};
  }}
  if (url === "/api/learning/path") {{
    return {{ ok: true, status: 200, json: async () => ({{ nodes: [] }}), text: async () => "" }};
  }}
  if (url === "/api/learning/cards") {{
    return {{ ok: true, status: 200, json: async () => ({{ learning_cards: [] }}), text: async () => "" }};
  }}
  if (url === "/api/membership/tiers") {{
    return {{ ok: true, status: 200, json: async () => ({{ tiers: [] }}), text: async () => "" }};
  }}
  return {{ ok: true, status: 200, json: async () => ({{}}), text: async () => "" }};
}};

const context = {{
  console,
  document,
  window: null,
  fetch: fetchStub,
  navigator: {{ mediaDevices: {{ getUserMedia: async () => ({{ getTracks: () => [] }}) }} }},
  RTCPeerConnection: function RTCPeerConnection() {{
    return {{
      addTrack() {{}},
      createDataChannel() {{ return {{ addEventListener() {{}}, close() {{}}, readyState: "open" }}; }},
      createOffer: async () => ({{ sdp: "stub" }}),
      setLocalDescription: async () => {{}},
      setRemoteDescription: async () => {{}},
      close() {{}},
    }};
  }},
  Intl,
  Date,
  JSON,
  setTimeout,
  clearTimeout,
}};
context.window = context;
context.globalThis = context;

async function flushAsync() {{
  for (let index = 0; index < 4; index += 1) {{
    await Promise.resolve();
  }}
  await new Promise((resolve) => setTimeout(resolve, 0));
}}

async function main() {{
  vm.createContext(context);
  vm.runInContext(source, context);
  await flushAsync();

  if (triggerGrowthClick && elements.commercialInterest.listeners.click) {{
    await elements.commercialInterest.listeners.click();
    await flushAsync();
  }}
  if (triggerMonetizationClick && monetizationButtons[0].listeners.click) {{
    await monetizationButtons[0].listeners.click();
    await flushAsync();
  }}

  process.stdout.write(JSON.stringify({{
    commercialSummaryHtml: elements.commercialInterestSummary.innerHTML,
    commercialStatusText: elements.commercialInterestStatus.textContent,
    gateBadgeText: elements.monetizationGateBadge.textContent,
    metricsHeadline: elements.monetizationMetricsHeadline.textContent,
    overviewText: elements.monetizationOverview.textContent,
    reasonHtml: elements.monetizationReasonList.innerHTML,
    metricsHtml: elements.monetizationMetricsList.innerHTML,
    offersHtml: elements.offerCatalogList.innerHTML,
    monetizationStatusText: elements.monetizationStatus.textContent,
    monetizationButtonDisabled: monetizationButtons[0].disabled,
    startSandboxDisabled: elements.startSandboxCheckoutBtn.disabled,
    confirmSandboxDisabled: elements.confirmSandboxPaymentBtn.disabled,
    fetchCalls,
  }}));
}}

main().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
        return run_realtime_harness(harness)

    def test_monetization_console_renders_stage_metrics_and_offer_cards(self):
        result = self.run_monetization_console_harness(
            growth_payload={"member_interest_count": 3},
            gate_payload={"gate_status": "blocked", "blocked_reasons": ["productization_not_active", "insufficient_feedback"]},
            metrics_payload={
                "event_count": 2,
                "business_lead_count": 1,
                "member_interest_count": 1,
                "course_interest_count": 1,
                "business_interest_count": 0,
                "pricing_view_count": 2,
                "offer_click_count": 1,
            },
            offers_payload={
                "catalog_notice": "All offers are interest-only previews.",
                "offers": [
                    {
                        "offer_id": "offer-membership-v0",
                        "category": "membership",
                        "title": "Membership preview",
                        "summary": "Complete reports and richer persona expression.",
                        "interest_only": True,
                        "enabled_event_types": ["member_interest", "pricing_view", "offer_click"],
                        "safety_note": "The preview sells content organization and learning experience, not outcomes.",
                    }
                ],
            },
        )

        self.assertEqual(result["gateBadgeText"], "等待上游阶段")
        self.assertIn("上游兴趣信号：3", result["commercialSummaryHtml"])
        self.assertIn("产品化阶段尚未进入实验", result["reasonHtml"])
        self.assertIn("已记录 2 条第 14 阶段事件，1 条商务线索。", result["metricsHeadline"])
        self.assertIn("权益浏览", result["metricsHtml"])
        self.assertIn("会员预览", result["offersHtml"])
        self.assertNotIn("Membership preview", result["offersHtml"])
        self.assertNotIn("All offers are interest-only previews", result["offersHtml"])
        self.assertNotIn("Complete reports and richer persona expression", result["offersHtml"])
        self.assertNotIn("The preview sells content organization", result["offersHtml"])
        self.assertIn("查看权益边界", result["offersHtml"])
        self.assertIn("当前仍是权益预览阶段", result["monetizationStatusText"])
        self.assertFalse(result["startSandboxDisabled"])
        self.assertFalse(result["confirmSandboxDisabled"])
        self.assertFalse(result["monetizationButtonDisabled"])

    def test_blocked_commercial_and_payment_actions_stay_clickable_with_feedback(self):
        result = self.run_monetization_console_harness(
            growth_payload={"member_interest_count": 1},
            gate_payload={"gate_status": "blocked", "blocked_reasons": ["productization_not_active"]},
            metrics_payload={
                "event_count": 0,
                "business_lead_count": 0,
                "member_interest_count": 0,
                "course_interest_count": 0,
                "business_interest_count": 0,
                "pricing_view_count": 0,
                "offer_click_count": 0,
            },
            offers_payload={
                "offers": [
                    {
                        "offer_id": "offer-membership-v0",
                        "category": "membership",
                        "title": "Membership preview",
                        "summary": "Complete reports and richer persona expression.",
                        "interest_only": True,
                        "enabled_event_types": ["pricing_view"],
                        "safety_note": "Interest only.",
                    }
                ]
            },
            trigger_monetization_click=True,
        )

        monetization_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/monetization/event"]
        self.assertEqual(monetization_posts, [])
        self.assertFalse(result["monetizationButtonDisabled"])
        self.assertIn("当前权益目录未开放这个快捷动作", result["monetizationStatusText"])

    def test_monetization_actions_keep_existing_post_shape_and_feedback(self):
        result = self.run_monetization_console_harness(
            growth_payload={"member_interest_count": 1},
            gate_payload={"gate_status": "blocked", "blocked_reasons": ["monetization_not_active"]},
            metrics_payload={
                "event_count": 0,
                "business_lead_count": 0,
                "member_interest_count": 0,
                "course_interest_count": 0,
                "business_interest_count": 0,
                "pricing_view_count": 0,
                "offer_click_count": 0,
            },
            offers_payload={"offers": []},
            growth_event_response={"stored": True, "metrics": {"member_interest_count": 4}},
            monetization_event_response={
                "stored": False,
                "blocked_reasons": ["monetization_not_active"],
                "gate": {"gate_status": "blocked", "blocked_reasons": ["monetization_not_active"]},
            },
            trigger_growth_click=True,
            trigger_monetization_click=True,
        )

        growth_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/growth/event"]
        monetization_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/monetization/event"]

        self.assertEqual(len(growth_posts), 1)
        self.assertEqual(growth_posts[0]["body"]["event_type"], "member_interest")
        self.assertEqual(growth_posts[0]["body"]["tester_id"], "T-001")
        self.assertEqual(monetization_posts, [])
        self.assertEqual(result["commercialStatusText"], "上游兴趣已记录，可继续查看右侧权益预览。")
        self.assertIn("当前权益目录未开放这个快捷动作", result["monetizationStatusText"])

    def test_monetization_event_uses_non_anonymous_fallback_without_tester_id(self):
        result = self.run_monetization_console_harness(
            growth_payload={"member_interest_count": 0},
            gate_payload={"gate_status": "blocked", "blocked_reasons": ["monetization_not_active"]},
            metrics_payload={
                "event_count": 0,
                "business_lead_count": 0,
                "member_interest_count": 0,
                "course_interest_count": 0,
                "business_interest_count": 0,
                "pricing_view_count": 0,
                "offer_click_count": 0,
            },
            offers_payload={
                "offers": [
                    {
                        "offer_id": "offer-membership-v0",
                        "category": "membership",
                        "title": "Membership preview",
                        "summary": "Complete reports and richer persona expression.",
                        "interest_only": True,
                        "enabled_event_types": ["member_interest"],
                        "safety_note": "Interest only.",
                    }
                ]
            },
            monetization_event_response={"stored": False, "blocked_reasons": ["monetization_not_active"]},
            trigger_monetization_click=True,
            tester_id="",
        )

        monetization_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/monetization/event"]
        self.assertEqual(len(monetization_posts), 1)
        self.assertNotEqual(monetization_posts[0]["body"]["visitor_id"], "anonymous")

    def test_monetization_button_disables_when_catalog_no_longer_supports_it(self):
        result = self.run_monetization_console_harness(
            growth_payload={"member_interest_count": 0},
            gate_payload={"gate_status": "blocked", "blocked_reasons": ["productization_not_active"]},
            metrics_payload={
                "event_count": 0,
                "business_lead_count": 0,
                "member_interest_count": 0,
                "course_interest_count": 0,
                "business_interest_count": 0,
                "pricing_view_count": 0,
                "offer_click_count": 0,
            },
            offers_payload={
                "offers": [
                    {
                        "offer_id": "offer-membership-v0",
                        "category": "membership",
                        "title": "Membership preview",
                        "summary": "Complete reports and richer persona expression.",
                        "interest_only": True,
                        "enabled_event_types": ["pricing_view"],
                        "safety_note": "Interest only.",
                    }
                ]
            },
        )

        self.assertFalse(result["monetizationButtonDisabled"])

    def run_commercial_payment_harness(
        self,
        payment_gate_payload: dict,
        tiers_payload: dict,
        payment_metrics_payload: dict | None = None,
        business_lead_response: dict | None = None,
        checkout_response: dict | None = None,
        confirm_response: dict | None = None,
        refund_response: dict | None = None,
        trigger_business_lead: bool = False,
        trigger_checkout: bool = False,
        trigger_confirm: bool = False,
        trigger_refund: bool = False,
    ) -> dict:
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(APP_JS))}, "utf8");
const paymentGatePayload = {json.dumps(payment_gate_payload)};
const tiersPayload = {json.dumps(tiers_payload)};
const paymentMetricsPayload = {json.dumps(payment_metrics_payload or {"order_count": 0, "pending_payment_count": 0, "paid_sandbox_count": 0, "refunded_count": 0, "blocked_order_count": 0})};
const businessLeadResponse = {json.dumps(business_lead_response or {"stored": False, "blocked_reasons": ["monetization_not_active"], "gate": {"gate_status": "blocked"}})};
const checkoutResponse = {json.dumps(checkout_response or {"stored": False, "blocked_reasons": ["payment_not_active"], "gate": payment_gate_payload})};
const confirmResponse = {json.dumps(confirm_response or checkout_response or {"stored": False, "blocked_reasons": ["payment_not_active"], "gate": payment_gate_payload})};
const refundResponse = {json.dumps(refund_response or confirm_response or checkout_response or {"stored": False, "blocked_reasons": ["payment_not_active"], "gate": payment_gate_payload})};
const triggerBusinessLead = {json.dumps(trigger_business_lead)};
const triggerCheckout = {json.dumps(trigger_checkout)};
const triggerConfirm = {json.dumps(trigger_confirm)};
const triggerRefund = {json.dumps(trigger_refund)};

function createClassList(initial = []) {{
  const set = new Set(initial);
  return {{
    add(name) {{ set.add(name); }},
    remove(name) {{ set.delete(name); }},
    toggle(name, force) {{
      if (force === undefined) {{
        if (set.has(name)) {{
          set.delete(name);
          return false;
        }}
        set.add(name);
        return true;
      }}
      if (force) {{
        set.add(name);
      }} else {{
        set.delete(name);
      }}
      return !!force;
    }},
    contains(name) {{ return set.has(name); }},
  }};
}}

function createElement(id, tagName = "div") {{
  let innerHtml = "";
  let textValue = "";
  return {{
    id,
    tagName: tagName.toUpperCase(),
    value: "",
    disabled: false,
    open: false,
    style: {{}},
    dataset: {{}},
    attributes: {{}},
    className: "",
    classList: createClassList(),
    listeners: {{}},
    get innerHTML() {{ return innerHtml; }},
    set innerHTML(value) {{ innerHtml = String(value); textValue = String(value); }},
    get textContent() {{ return textValue; }},
    set textContent(value) {{ textValue = String(value); innerHtml = String(value); }},
    addEventListener(type, handler) {{ this.listeners[type] = handler; }},
    scrollIntoView(options) {{ this.scrollOptions = options; }},
    setAttribute(name, value) {{
      this.attributes[name] = String(value);
      if (name.startsWith("data-")) {{
        const key = name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
        this.dataset[key] = String(value);
      }}
    }},
    getAttribute(name) {{
      return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null;
    }},
    removeAttribute(name) {{ delete this.attributes[name]; }},
  }};
}}

const elementIds = [
  "connectBtn",
  "disconnectBtn",
  "interruptBtn",
  "modeSelect",
  "testerId",
  "inviteCode",
  "status",
  "textQuestion",
  "runTextInterpretBtn",
  "textInterpretStatus",
  "betaNotice",
  "opsPauseNotice",
  "publicFeedbackNotice",
  "visitorNickname",
  "saveVisitorProfileBtn",
  "visitorProfileStatus",
  "transcript",
  "toolLog",
  "interpretationPreview",
  "explainResult",
  "debugDetails",
  "debugJson",
  "learningMaterials",
  "personaCards",
  "personaCardsToggle",
  "learningCards",
  "learningPathPanel",
  "learningPathSummary",
  "learningPathRecommended",
  "learningPathNodes",
  "learningPathDetail",
  "learningPathStatus",
  "safetyState",
  "feedbackType",
  "feedbackNote",
  "submitFeedbackBtn",
  "feedbackStatus",
  "canaryStatusBadge",
  "canaryOverview",
  "canaryProgressLabel",
  "canaryProgressBarFill",
  "canaryMilestones",
  "canaryTaskList",
  "commercialInterest",
  "commercialInterestSummary",
  "commercialInterestStatus",
  "monetizationGateBadge",
  "monetizationMetricsHeadline",
  "monetizationOverview",
  "monetizationReasonList",
  "monetizationMetricsList",
  "offerCatalogList",
  "monetizationStatus",
  "commercialPathSteps",
  "commercialPathSummary",
  "commercialPathMetrics",
  "businessLeadNickname",
  "businessLeadChannel",
  "businessLeadSummary",
  "submitBusinessLeadBtn",
  "businessLeadStatus",
  "businessLeadOutcome",
  "membershipTiersList",
  "paymentGateStatus",
  "paymentGateBadge",
  "paymentGateReasonList",
  "paymentCapabilitiesList",
  "paymentMetricsList",
  "paymentTierSelect",
  "startSandboxCheckoutBtn",
  "confirmSandboxPaymentBtn",
  "failSandboxPaymentBtn",
  "cancelSandboxOrderBtn",
  "refundSandboxOrderBtn",
  "sandboxOrderStatus",
  "sandboxOrderDetail",
  "shareReport",
  "shareReportMeta",
  "shareReportLead",
  "shareReportCards",
  "shareReportCopyStatus",
  "copyShareReportTextBtn",
  "copyShareReportHtmlBtn",
  "shareReportDraftDetails",
  "shareReportDraftMeta",
  "shareReportDraftCards",
  "copyShareReportDraftBtn",
  "remoteAudio",
  "questionPanel",
  "feedbackPanel",
  "experimentsPanel",
];

const elements = Object.fromEntries(elementIds.map((id) => [id, createElement(id, id === "experimentsPanel" ? "details" : "div")]));
elements.modeSelect.value = "plain";
elements.feedbackType.value = "helpful";
elements.testerId.value = "T-900";
elements.businessLeadNickname.value = "书店主理人";
elements.businessLeadChannel.value = "线下活动";
elements.businessLeadSummary.value = "想做 20 人传统文化工作坊。";

const document = {{
  documentElement: {{ dataset: {{ language: "zh" }} }},
  getElementById(id) {{ return elements[id] || null; }},
  querySelector() {{ return null; }},
  querySelectorAll(selector) {{
    if (selector === ".monetizationInterest" || selector === ".app-nav a" || selector === "[data-offer-preview]") {{
      return [];
    }}
    return [];
  }},
  addEventListener() {{}},
}};

const fetchCalls = [];
const fetchStub = async (url, options = {{}}) => {{
  const body = typeof options.body === "string" ? JSON.parse(options.body) : null;
  fetchCalls.push({{ url, method: options.method || "GET", body }});
  if (url === "/api/beta/config") {{
    return {{ ok: true, status: 200, json: async () => ({{ tester_notice: "Beta notice" }}), text: async () => "" }};
  }}
  if (url === "/api/beta/report") {{
    return {{ ok: true, status: 200, json: async () => ({{}}), text: async () => "" }};
  }}
  if (url === "/api/ops/status") {{
    return {{ ok: true, status: 200, json: async () => ({{ status: "canary", blocked_reasons: [] }}), text: async () => "" }};
  }}
  if (url === "/api/public/status") {{
    return {{ ok: true, status: 200, json: async () => ({{ launch_status: "blocked" }}), text: async () => "" }};
  }}
  if (url === "/api/productization/gate") {{
    return {{ ok: true, status: 200, json: async () => ({{ gate_status: "blocked" }}), text: async () => "" }};
  }}
  if (url === "/api/growth/metrics") {{
    return {{ ok: true, status: 200, json: async () => ({{ member_interest_count: 2 }}), text: async () => "" }};
  }}
  if (url === "/api/monetization/gate") {{
    return {{ ok: true, status: 200, json: async () => ({{ gate_status: "experiment", blocked_reasons: [] }}), text: async () => "" }};
  }}
  if (url === "/api/monetization/metrics") {{
    return {{ ok: true, status: 200, json: async () => ({{ event_count: 3, business_lead_count: 0, member_interest_count: 1, course_interest_count: 0, business_interest_count: 0, pricing_view_count: 1, offer_click_count: 1 }}), text: async () => "" }};
  }}
  if (url === "/api/monetization/offers") {{
    return {{ ok: true, status: 200, json: async () => ({{ offers: [] }}), text: async () => "" }};
  }}
  if (url === "/api/business/lead") {{
    return {{ ok: true, status: 200, json: async () => businessLeadResponse, text: async () => "" }};
  }}
  if (url === "/api/payment/gate") {{
    return {{ ok: true, status: 200, json: async () => paymentGatePayload, text: async () => "" }};
  }}
  if (url === "/api/payment/metrics") {{
    return {{ ok: true, status: 200, json: async () => paymentMetricsPayload, text: async () => "" }};
  }}
  if (url === "/api/membership/tiers") {{
    return {{ ok: true, status: 200, json: async () => tiersPayload, text: async () => "" }};
  }}
  if (url === "/api/payment/checkout") {{
    return {{ ok: true, status: 200, json: async () => checkoutResponse, text: async () => "" }};
  }}
  if (url === "/api/payment/sandbox/confirm") {{
    return {{ ok: true, status: 200, json: async () => confirmResponse, text: async () => "" }};
  }}
  if (url === "/api/payment/refund") {{
    return {{ ok: true, status: 200, json: async () => refundResponse, text: async () => "" }};
  }}
  if (url === "/api/canary/run/config") {{
    return {{ ok: true, status: 200, json: async () => ({{ tester_tasks: [] }}), text: async () => "" }};
  }}
  if (url.startsWith("/api/canary/tasks/status")) {{
    return {{ ok: true, status: 200, json: async () => ({{}}), text: async () => "" }};
  }}
  if (url === "/api/learning/path") {{
    return {{ ok: true, status: 200, json: async () => ({{ nodes: [] }}), text: async () => "" }};
  }}
  if (url === "/api/learning/cards") {{
    return {{ ok: true, status: 200, json: async () => ({{ learning_cards: [] }}), text: async () => "" }};
  }}
  return {{ ok: true, status: 200, json: async () => ({{}}), text: async () => "" }};
}};

const context = {{
  console,
  document,
  window: null,
  fetch: fetchStub,
  navigator: {{ mediaDevices: {{ getUserMedia: async () => ({{ getTracks: () => [] }}) }} }},
  RTCPeerConnection: function RTCPeerConnection() {{
    return {{
      addTrack() {{}},
      createDataChannel() {{ return {{ addEventListener() {{}}, close() {{}}, readyState: "open" }}; }},
      createOffer: async () => ({{ sdp: "stub" }}),
      setLocalDescription: async () => {{}},
      setRemoteDescription: async () => {{}},
      close() {{}},
    }};
  }},
  Intl,
  Date,
  JSON,
  Math,
  setTimeout,
  clearTimeout,
}};
context.window = context;
context.globalThis = context;

async function flushAsync() {{
  for (let index = 0; index < 5; index += 1) {{
    await Promise.resolve();
  }}
  await new Promise((resolve) => setTimeout(resolve, 0));
}}

async function main() {{
  vm.createContext(context);
  vm.runInContext(source, context);
  await flushAsync();

  if (triggerBusinessLead && elements.submitBusinessLeadBtn.listeners.click) {{
    await elements.submitBusinessLeadBtn.listeners.click();
    await flushAsync();
  }}
  if (triggerCheckout && elements.startSandboxCheckoutBtn.listeners.click) {{
    await elements.startSandboxCheckoutBtn.listeners.click();
    await flushAsync();
  }}
  if (triggerConfirm && elements.confirmSandboxPaymentBtn.listeners.click) {{
    await elements.confirmSandboxPaymentBtn.listeners.click();
    await flushAsync();
  }}
  if (triggerRefund && elements.refundSandboxOrderBtn.listeners.click) {{
    await elements.refundSandboxOrderBtn.listeners.click();
    await flushAsync();
  }}

  process.stdout.write(JSON.stringify({{
    pathStepsHtml: elements.commercialPathSteps.innerHTML,
    pathSummaryText: elements.commercialPathSummary.textContent,
    pathMetricsHtml: elements.commercialPathMetrics.innerHTML,
    businessLeadStatus: elements.businessLeadStatus.textContent,
    businessLeadOutcomeHtml: elements.businessLeadOutcome.innerHTML,
    membershipHtml: elements.membershipTiersList.innerHTML,
    paymentGateText: elements.paymentGateStatus.textContent,
    paymentGateBadgeText: elements.paymentGateBadge.textContent,
    paymentReasonsHtml: elements.paymentGateReasonList.innerHTML,
    capabilitiesHtml: elements.paymentCapabilitiesList.innerHTML,
    paymentMetricsHtml: elements.paymentMetricsList.innerHTML,
    selectedTier: elements.paymentTierSelect.value,
    startDisabled: elements.startSandboxCheckoutBtn.disabled,
    confirmDisabled: elements.confirmSandboxPaymentBtn.disabled,
    refundDisabled: elements.refundSandboxOrderBtn.disabled,
    sandboxStatus: elements.sandboxOrderStatus.textContent,
    sandboxDetailHtml: elements.sandboxOrderDetail.innerHTML,
    fetchCalls,
  }}));
}}

main().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
        return run_realtime_harness(harness)

    def test_commercial_payment_path_renders_real_gate_tiers_and_blocked_reason(self):
        result = self.run_commercial_payment_harness(
            payment_gate_payload={
                "gate_status": "blocked",
                "blocked_reasons": ["insufficient_monetization_interest"],
                "enabled_capabilities": [],
            },
            tiers_payload={
                "tiers": [
                    {
                        "tier_id": "tier-membership-v0",
                        "category": "membership",
                        "title": "Membership sandbox preview",
                        "summary": "Complete report draft, more learning cards, case library preview, and source-card expansion.",
                        "sandbox_only": True,
                        "high_risk_unlocked": False,
                        "unreviewed_complex_rules_unlocked": False,
                        "rights_preview": ["complete_report", "learning_card_extension", "case_library_preview"],
                    }
                ]
            },
        )

        self.assertEqual(result["paymentGateBadgeText"], "等待前置门槛")
        self.assertIn("会员兴趣、权益浏览或权益点击还没有达到沙箱门槛", result["paymentReasonsHtml"])
        self.assertIn("完整报告草稿", result["membershipHtml"])
        self.assertIn("仅沙箱演示", result["membershipHtml"])
        self.assertIn("当前无可用支付能力", result["capabilitiesHtml"])
        self.assertFalse(result["startDisabled"])
        self.assertFalse(result["confirmDisabled"])
        self.assertIn("当前路径会展示真实接口状态", result["pathSummaryText"])
        self.assertNotIn("Membership sandbox preview", result["membershipHtml"])

    def test_blocked_sandbox_checkout_button_stays_clickable_and_explains_gate(self):
        result = self.run_commercial_payment_harness(
            payment_gate_payload={
                "gate_status": "blocked",
                "blocked_reasons": ["insufficient_monetization_interest"],
                "enabled_capabilities": [],
            },
            tiers_payload={
                "tiers": [
                    {
                        "tier_id": "tier-membership-v0",
                        "category": "membership",
                        "title": "Membership sandbox preview",
                        "summary": "Complete report draft, more learning cards, case library preview, and source-card expansion.",
                        "sandbox_only": True,
                        "high_risk_unlocked": False,
                        "unreviewed_complex_rules_unlocked": False,
                        "rights_preview": ["complete_report"],
                    }
                ]
            },
            trigger_checkout=True,
        )

        checkout_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/payment/checkout"]
        self.assertEqual(checkout_posts, [])
        self.assertFalse(result["startDisabled"])
        self.assertIn("沙箱订单暂不可创建", result["sandboxStatus"])
        self.assertIn("会员兴趣、权益浏览或权益点击还没有达到沙箱门槛", result["sandboxDetailHtml"])

    def test_sandbox_checkout_without_tier_stays_clickable_and_explains_missing_tier(self):
        result = self.run_commercial_payment_harness(
            payment_gate_payload={
                "gate_status": "sandbox",
                "blocked_reasons": [],
                "enabled_capabilities": ["mock_sandbox_checkout"],
            },
            tiers_payload={"tiers": []},
            trigger_checkout=True,
        )

        checkout_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/payment/checkout"]
        self.assertEqual(checkout_posts, [])
        self.assertFalse(result["startDisabled"])
        self.assertIn("暂无可用会员层级", result["sandboxStatus"])
        self.assertIn("缺少权益层", result["sandboxDetailHtml"])

    def test_business_lead_submit_posts_real_payload_and_renders_result(self):
        result = self.run_commercial_payment_harness(
            payment_gate_payload={"gate_status": "blocked", "blocked_reasons": ["insufficient_monetization_interest"]},
            tiers_payload={"tiers": []},
            business_lead_response={
                "stored": True,
                "lead": {
                    "lead_id": "business_lead_001",
                    "contact_nickname": "书店主理人",
                    "channel": "线下活动",
                },
                "gate": {"gate_status": "experiment", "blocked_reasons": []},
                "metrics": {"event_count": 3, "business_lead_count": 1, "member_interest_count": 1, "pricing_view_count": 1, "offer_click_count": 1},
            },
            trigger_business_lead=True,
        )

        lead_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/business/lead"]
        self.assertEqual(len(lead_posts), 1)
        self.assertEqual(lead_posts[0]["body"]["visitor_id"], "T-900")
        self.assertEqual(lead_posts[0]["body"]["contact_nickname"], "书店主理人")
        self.assertEqual(lead_posts[0]["body"]["channel"], "线下活动")
        self.assertEqual(lead_posts[0]["body"]["offer_id"], "offer-b2b-v0")
        self.assertIn("商务线索已记录", result["businessLeadStatus"])
        self.assertIn("business_lead_001", result["businessLeadOutcomeHtml"])
        self.assertIn("已写入实验线索池", result["businessLeadOutcomeHtml"])
        self.assertIn("提交商务线索", result["pathStepsHtml"])

    def test_sandbox_checkout_success_and_refund_path_updates_buttons_and_order_detail(self):
        result = self.run_commercial_payment_harness(
            payment_gate_payload={
                "gate_status": "sandbox",
                "blocked_reasons": [],
                "enabled_capabilities": ["mock_sandbox_checkout", "sandbox_payment_confirm", "sandbox_refund"],
            },
            tiers_payload={
                "tiers": [
                    {
                        "tier_id": "tier-membership-v0",
                        "category": "membership",
                        "title": "Membership sandbox preview",
                        "summary": "Complete report draft, more learning cards, case library preview, and source-card expansion.",
                        "sandbox_only": True,
                        "high_risk_unlocked": False,
                        "unreviewed_complex_rules_unlocked": False,
                        "rights_preview": ["complete_report"],
                    }
                ]
            },
            checkout_response={
                "stored": True,
                "order": {
                    "order_id": "sandbox_order_001",
                    "tier_id": "tier-membership-v0",
                    "order_status": "pending_payment",
                    "provider": "mock_sandbox",
                    "currency": "CNY",
                    "amount_cents": 0,
                    "timestamp": "2026-05-12T00:00:00Z",
                },
                "event": {"event_type": "checkout_started"},
                "gate": {"gate_status": "sandbox", "blocked_reasons": []},
                "metrics": {"order_count": 1, "pending_payment_count": 1, "paid_sandbox_count": 0, "refunded_count": 0, "blocked_order_count": 0},
            },
            confirm_response={
                "stored": True,
                "order": {
                    "order_id": "sandbox_order_001",
                    "tier_id": "tier-membership-v0",
                    "order_status": "paid_sandbox",
                    "provider": "mock_sandbox",
                    "currency": "CNY",
                    "amount_cents": 0,
                    "timestamp": "2026-05-12T00:01:00Z",
                },
                "event": {"event_type": "sandbox_paid"},
                "gate": {"gate_status": "sandbox", "blocked_reasons": []},
                "metrics": {"order_count": 2, "pending_payment_count": 1, "paid_sandbox_count": 1, "refunded_count": 0, "blocked_order_count": 0},
            },
            refund_response={
                "stored": True,
                "order": {
                    "order_id": "sandbox_order_001",
                    "tier_id": "tier-membership-v0",
                    "order_status": "refunded",
                    "provider": "mock_sandbox",
                    "currency": "CNY",
                    "amount_cents": 0,
                    "reason": "frontend_refund_demo",
                    "timestamp": "2026-05-12T00:02:00Z",
                },
                "event": {"event_type": "refund_completed"},
                "gate": {"gate_status": "sandbox", "blocked_reasons": []},
                "metrics": {"order_count": 3, "pending_payment_count": 1, "paid_sandbox_count": 1, "refunded_count": 1, "blocked_order_count": 0},
            },
            trigger_checkout=True,
            trigger_confirm=True,
            trigger_refund=True,
        )

        checkout_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/payment/checkout"]
        confirm_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/payment/sandbox/confirm"]
        refund_posts = [call for call in result["fetchCalls"] if call["url"] == "/api/payment/refund"]
        self.assertEqual(len(checkout_posts), 1)
        self.assertEqual(checkout_posts[0]["body"]["visitor_id"], "T-900")
        self.assertEqual(checkout_posts[0]["body"]["tier_id"], "tier-membership-v0")
        self.assertEqual(len(confirm_posts), 1)
        self.assertEqual(confirm_posts[0]["body"]["order_id"], "sandbox_order_001")
        self.assertEqual(confirm_posts[0]["body"]["outcome"], "success")
        self.assertEqual(len(refund_posts), 1)
        self.assertEqual(refund_posts[0]["body"]["reason"], "frontend_refund_demo")
        self.assertIn("订单 sandbox_order_001：已退款", result["sandboxStatus"])
        self.assertIn("沙箱订单 001", result["sandboxDetailHtml"])
        self.assertIn("会员沙箱预览", result["sandboxDetailHtml"])
        self.assertIn("沙箱模拟", result["sandboxDetailHtml"])
        self.assertIn("前端退款演示", result["sandboxDetailHtml"])
        self.assertIn("沙箱退款完成", result["sandboxDetailHtml"])
        self.assertFalse(result["confirmDisabled"])
        self.assertFalse(result["refundDisabled"])
        self.assertIn("沙箱成功", result["pathMetricsHtml"])

    def test_schema_files_exist_for_realtime_phase(self):
        for schema_name in [
            "realtime_session.request.schema.json",
            "liuren_interpret_tool.request.schema.json",
            "liuren_interpret_tool.response.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
