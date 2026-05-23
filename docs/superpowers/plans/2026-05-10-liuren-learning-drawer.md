# Liuren Learning Drawer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the static “学习闯关” list in `/app` with a usable right-rail learning drawer that recommends the next node, renders clickable node cards, and shows an in-drawer detail view with graceful fallback states.

**Architecture:** Keep the existing `/app` workbench structure and backend APIs. Move the learning path panel into the right rail as its own `details` drawer, then enhance `static/realtime/app.js` with a small learning-path state machine that loads `/api/learning/path` plus `/api/learning/cards`, derives display metadata, and re-renders the drawer based on the selected node and fetch outcomes.

**Tech Stack:** Static HTML, CSS, vanilla browser JavaScript, Python `unittest` contract tests with Node VM harnesses, existing FastAPI endpoints `/api/learning/path`, `/api/learning/cards`, and `/api/learning/progress`.

---

## File Map

- Modify: `static/realtime/index.html`
  - Move `learningPathPanel` out of `experimentsPanel` and into `aside#supportPanel`.
  - Replace the static list container with explicit drawer subregions for summary, recommendation, node list, detail, and status feedback.
- Modify: `static/realtime/styles.css`
  - Add right-rail drawer layout and interaction styles for the learning drawer, recommended card, node buttons, status pills, and detail area.
- Modify: `static/realtime/app.js`
  - Extend state for learning drawer data.
  - Fetch learning path and learning cards.
  - Build node/card join helpers.
  - Render the recommendation, node list, detail area, and degraded states.
  - Wire node selection and progress recording.
- Modify: `tests/test_realtime_frontend.py`
  - Add static HTML contract tests for drawer placement and required ids.
  - Add a Node harness for learning drawer rendering, selection, and degraded states.

## Shared Constraints

- Do not add a new route or page.
- Do not add a new backend endpoint.
- Keep `experimentsPanel` for canary, monetization, payment, and debug content only.
- Keep TDD discipline: write a failing test, run it and confirm failure, then implement minimal code to pass.
- If `git rev-parse --is-inside-work-tree` fails in this workspace, skip commit steps and continue without trying to force git.

### Task 1: Lock The New Drawer Contract In Tests

**Files:**
- Modify: `tests/test_realtime_frontend.py`
- Test: `tests/test_realtime_frontend.py`

- [ ] **Step 1: Write the failing static layout contract test**

Add a new test near the existing layout tests:

```python
    def test_learning_path_panel_moves_into_support_rail_as_drawer(self):
        html = (ROOT / "static" / "realtime" / "index.html").read_text(encoding="utf-8")

        support_start = html.index('id="supportPanel"')
        learning_materials_start = html.index('id="learningMaterials"')
        learning_path_start = html.index('id="learningPathPanel"')
        feedback_start = html.index('id="feedbackPanel"')
        experiments_start = html.index('id="experimentsPanel"')

        self.assertIn('<details id="learningPathPanel"', html)
        self.assertIn('<summary>学习闯关</summary>', html)
        self.assertGreater(learning_path_start, learning_materials_start)
        self.assertGreater(learning_path_start, support_start)
        self.assertLess(learning_path_start, feedback_start)
        self.assertLess(learning_path_start, experiments_start)

        for element_id in [
            "learningPathSummary",
            "learningPathRecommended",
            "learningPathNodes",
            "learningPathDetail",
            "learningPathStatus",
        ]:
            self.assertIn(f'id="{element_id}"', html)
```

- [ ] **Step 2: Run the new layout test and verify it fails**

Run:

```bash
python -m pytest tests/test_realtime_frontend.py -k "learning_path_panel_moves_into_support_rail_as_drawer" -v
```

Expected: `FAIL` because `learningPathPanel` is still an `<article>` inside `experimentsPanel` and the new ids do not exist yet.

- [ ] **Step 3: Add a reusable learning drawer harness plus failing interaction tests**

Add a new helper to the test class that stubs both fetches and simulates clicks:

```python
    def run_learning_path_harness(
        self,
        path_payload: dict,
        cards_payload: dict | None,
        click_node_id: str | None = None,
        trigger_recommended: bool = False,
    ) -> dict:
        harness = f"""
const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync({json.dumps(str(APP_JS))}, "utf8");
const pathPayload = {json.dumps(path_payload)};
const cardsPayload = {json.dumps(cards_payload)};
const clickNodeId = {json.dumps(click_node_id)};
const triggerRecommended = {json.dumps(trigger_recommended)};

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
    toArray() {{ return Array.from(set).sort(); }},
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
    addEventListener(type, handler) {{ this.listeners[type] = handler; }},
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
  }};
}}

const elementIds = [
  "connectBtn", "disconnectBtn", "interruptBtn", "modeSelect", "testerId", "inviteCode", "status",
  "textQuestion", "runTextInterpretBtn", "textInterpretStatus", "betaNotice", "opsPauseNotice",
  "publicFeedbackNotice", "visitorNickname", "saveVisitorProfileBtn", "visitorProfileStatus",
  "transcript", "toolLog", "interpretationPreview", "explainResult", "debugDetails", "debugJson",
  "learningMaterials", "personaCards", "personaCardsToggle", "learningCards", "learningPathPanel",
  "learningPathSummary", "learningPathRecommended", "learningPathNodes", "learningPathDetail",
  "learningPathStatus", "learningPathList", "safetyState", "feedbackType", "feedbackNote",
  "submitFeedbackBtn", "feedbackStatus", "canaryTaskList", "commercialInterest",
  "commercialInterestStatus", "offerCatalogList", "monetizationStatus", "businessLeadNickname",
  "businessLeadChannel", "businessLeadSummary", "submitBusinessLeadBtn", "businessLeadStatus",
  "membershipTiersList", "paymentGateStatus", "paymentTierSelect", "startSandboxCheckoutBtn",
  "confirmSandboxPaymentBtn", "failSandboxPaymentBtn", "cancelSandboxOrderBtn",
  "refundSandboxOrderBtn", "sandboxOrderStatus", "shareReport", "reportText", "pdfReportDraft",
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
    return {{ ok: true, json: async () => pathPayload }};
  }}
  if (url === "/api/learning/cards") {{
    if (cardsPayload === null) {{
      return {{ ok: false, status: 503, json: async () => ({{}}), text: async () => "" }};
    }}
    return {{ ok: true, json: async () => cardsPayload }};
  }}
  if (url === "/api/learning/progress") {{
    return {{ ok: true, json: async () => ({{ stored: false, blocked_reasons: ["productization_not_active"] }}) }};
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

vm.createContext(context);
vm.runInContext(source + "\\n;globalThis.__learningTestExports = { loadLearningPath, state, els };", context);

await context.__learningTestExports.loadLearningPath();

if (clickNodeId && typeof elements.learningPathNodes.listeners.click === "function") {{
  elements.learningPathNodes.listeners.click({{
    target: {{ closest: () => ({{ dataset: {{ nodeId: clickNodeId }} }}) }},
  }});
}}

if (triggerRecommended && typeof elements.learningPathRecommended.listeners.click === "function") {{
  elements.learningPathRecommended.listeners.click({{
    target: {{ closest: () => ({{ dataset: {{ action: "start-learning" }} }}) }},
    preventDefault() {{}},
  }});
}}

process.stdout.write(JSON.stringify({{
  summaryHtml: elements.learningPathSummary.innerHTML,
  recommendedHtml: elements.learningPathRecommended.innerHTML,
  nodesHtml: elements.learningPathNodes.innerHTML,
  detailHtml: elements.learningPathDetail.innerHTML,
  statusText: elements.learningPathStatus.textContent,
  panelOpen: elements.learningPathPanel.open,
  fetchCalls,
}}));
"""
        return run_realtime_harness(harness)
```

Add these tests below it:

```python
    def test_learning_path_recommends_first_approved_node_and_renders_buttons(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {"node_id": "LP-A", "topic": "four_lessons", "title": "Four lessons", "learning_card_ids": ["LC-001"], "source_ids": ["RC-013"], "example_case_ids": ["GC-001"], "review_status": "approved_for_mvp", "unlocked_outputs": ["learning_note"]},
                    {"node_id": "LP-B", "topic": "nine_rules", "title": "Nine methods", "learning_card_ids": ["LC-003"], "source_ids": ["RC-060"], "example_case_ids": ["GC-060"], "review_status": "research_only", "unlocked_outputs": ["research_note"]},
                ]
            },
            cards_payload={
                "learning_cards": [
                    {"card_id": "LC-001", "title": "四课结构", "summary": "看四课骨架。", "tags": ["四课"], "source_ids": ["RC-013"]},
                    {"card_id": "LC-003", "title": "九宗门", "summary": "研究性内容。", "tags": ["三传"], "source_ids": ["RC-060"]},
                ]
            },
        )

        self.assertIn("推荐下一步", result["recommendedHtml"])
        self.assertIn("开始学习", result["recommendedHtml"])
        self.assertIn("可学", result["recommendedHtml"])
        self.assertIn("研究中", result["nodesHtml"])

    def test_learning_path_clicking_node_updates_detail(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {"node_id": "LP-A", "topic": "four_lessons", "title": "Four lessons", "learning_card_ids": ["LC-001"], "source_ids": ["RC-013"], "example_case_ids": ["GC-001"], "review_status": "approved_for_mvp", "unlocked_outputs": ["learning_note"]},
                ]
            },
            cards_payload={
                "learning_cards": [
                    {"card_id": "LC-001", "title": "四课结构", "summary": "看四课骨架。", "tags": ["四课"], "source_ids": ["RC-013"]},
                ]
            },
            click_node_id="LP-A",
        )

        self.assertIn("Four lessons", result["detailHtml"])
        self.assertIn("四课结构", result["detailHtml"])
        self.assertIn("标记已读", result["detailHtml"])

    def test_learning_path_research_only_node_shows_read_only_state(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {"node_id": "LP-B", "topic": "nine_rules", "title": "Nine methods", "learning_card_ids": ["LC-003"], "source_ids": ["RC-060"], "example_case_ids": ["GC-060"], "review_status": "research_only", "unlocked_outputs": ["research_note"]},
                ]
            },
            cards_payload={
                "learning_cards": [
                    {"card_id": "LC-003", "title": "九宗门", "summary": "研究性内容。", "tags": ["三传"], "source_ids": ["RC-060"]},
                ]
            },
            click_node_id="LP-B",
        )

        self.assertIn("当前仅供研究参考", result["detailHtml"])
        self.assertIn("暂不可学", result["detailHtml"])

    def test_learning_path_cards_failure_keeps_nodes_and_shows_degraded_detail(self):
        result = self.run_learning_path_harness(
            path_payload={
                "nodes": [
                    {"node_id": "LP-A", "topic": "four_lessons", "title": "Four lessons", "learning_card_ids": ["LC-001"], "source_ids": ["RC-013"], "example_case_ids": ["GC-001"], "review_status": "approved_for_mvp", "unlocked_outputs": ["learning_note"]},
                ]
            },
            cards_payload=None,
            click_node_id="LP-A",
        )

        self.assertIn("Four lessons", result["nodesHtml"])
        self.assertIn("关联学习卡暂不可用", result["detailHtml"])
```

- [ ] **Step 4: Run the learning drawer tests and verify they fail**

Run:

```bash
python -m pytest tests/test_realtime_frontend.py -k "learning_path" -v
```

Expected: `FAIL` because the new DOM ids, recommendation UI, node click handling, and degraded card behavior do not exist yet.

- [ ] **Step 5: Commit the red tests if git is available**

Run:

```bash
git rev-parse --is-inside-work-tree
```

If the command prints `true`, then run:

```bash
git add tests/test_realtime_frontend.py
git commit -m "test: define learning drawer frontend contract"
```

If the command errors or does not print `true`, skip the commit in this workspace.

### Task 2: Move The Drawer Into The Right Rail And Create Its DOM Shell

**Files:**
- Modify: `static/realtime/index.html`
- Test: `tests/test_realtime_frontend.py`

- [ ] **Step 1: Replace the old experiments-panel card with a right-rail drawer shell**

In `aside#supportPanel`, insert this block after `#learningMaterials` and before `#feedbackPanel`:

```html
          <details id="learningPathPanel" class="panel rail-card learning-path-panel">
            <summary>学习闯关</summary>
            <div class="learning-path-shell">
              <p id="learningPathSummary" class="muted">从基础结构到安全边界，按节点学习。</p>
              <article id="learningPathRecommended" class="learning-path-recommended">
                <p class="muted">推荐学习项加载中。</p>
              </article>
              <div id="learningPathNodes" class="learning-path-nodes" aria-live="polite"></div>
              <article id="learningPathDetail" class="learning-path-detail">
                <p class="muted">选择一个节点查看详情。</p>
              </article>
              <p id="learningPathStatus" class="muted"></p>
            </div>
          </details>
```

Remove the old card from `#experimentsPanel`:

```html
          <article id="learningPathPanel" class="panel">
            <p class="eyebrow">学习</p>
            <h2>学习闯关</h2>
            <div id="learningPathList" class="stack"></div>
          </article>
```

- [ ] **Step 2: Run the static layout contract test and verify it passes**

Run:

```bash
python -m pytest tests/test_realtime_frontend.py -k "learning_path_panel_moves_into_support_rail_as_drawer" -v
```

Expected: `PASS`

- [ ] **Step 3: Keep a compatibility placeholder for old JS references until the JS task lands**

If the script still needs `learningPathList` before the JS refactor, keep a hidden fallback inside the drawer shell temporarily:

```html
              <div id="learningPathList" class="hidden" aria-hidden="true"></div>
```

This should be removed in the JS task once all references are switched to `learningPathNodes`.

- [ ] **Step 4: Run the broader static frontend suite to verify only JS behavior tests still fail**

Run:

```bash
python -m pytest tests/test_realtime_frontend.py -k "static_realtime_page or learning_path" -v
```

Expected: static layout tests pass; interactive learning drawer tests still fail.

- [ ] **Step 5: Commit the HTML move if git is available**

Run:

```bash
git rev-parse --is-inside-work-tree
```

If the command prints `true`, then run:

```bash
git add static/realtime/index.html tests/test_realtime_frontend.py
git commit -m "feat: move learning path drawer into support rail"
```

If the command errors or does not print `true`, skip the commit in this workspace.

### Task 3: Add The Drawer Styles And Interaction States

**Files:**
- Modify: `static/realtime/styles.css`
- Test: `tests/test_realtime_frontend.py`

- [ ] **Step 1: Add the new drawer layout and card rules**

Append these rules near the other right-rail component styles:

```css
.learning-path-panel summary {
  color: #141820;
  font-weight: 700;
}

.learning-path-shell {
  display: grid;
  gap: 14px;
  margin-top: 12px;
}

.learning-path-recommended,
.learning-path-detail {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px;
  background: linear-gradient(180deg, rgba(255, 243, 213, 0.6), rgba(255, 254, 250, 0.96));
}

.learning-path-nodes {
  display: grid;
  gap: 10px;
}

.learning-path-node {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px 14px;
  background: #fffefa;
  text-align: left;
  cursor: pointer;
  transition: border-color 180ms ease, transform 180ms ease, box-shadow 180ms ease;
}

.learning-path-node:hover,
.learning-path-node:focus-visible,
.learning-path-node[data-selected="true"] {
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(183, 121, 31, 0.14);
  outline: 0;
}

.learning-path-meta,
.learning-path-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  font-size: 12px;
  font-weight: 700;
}

.status-pill.available {
  border-color: var(--gold);
  background: var(--gold-soft);
  color: #7a4b10;
}

.status-pill.research {
  border-color: #d5d0c6;
  background: #f3efe7;
  color: #6b6256;
}
```

- [ ] **Step 2: Add mobile-safe spacing adjustments**

Inside the existing `@media (max-width: 640px)` block, add:

```css
  .learning-path-node,
  .learning-path-recommended,
  .learning-path-detail {
    padding: 12px;
  }

  .learning-path-meta,
  .learning-path-actions {
    flex-direction: column;
    align-items: stretch;
  }
```

- [ ] **Step 3: Add a static CSS contract assertion**

Extend `test_static_realtime_page_uses_workbench_layout` with:

```python
        for rule in [
            ".learning-path-panel",
            ".learning-path-shell",
            ".learning-path-node",
            ".learning-path-detail",
            ".status-pill.available",
            ".status-pill.research",
        ]:
            self.assertIn(rule, css)
```

- [ ] **Step 4: Run the static CSS contract and verify it passes**

Run:

```bash
python -m pytest tests/test_realtime_frontend.py -k "static_realtime_page_uses_workbench_layout" -v
```

Expected: `PASS`

- [ ] **Step 5: Commit the styles if git is available**

Run:

```bash
git rev-parse --is-inside-work-tree
```

If the command prints `true`, then run:

```bash
git add static/realtime/styles.css tests/test_realtime_frontend.py
git commit -m "feat: style learning drawer interactions"
```

If the command errors or does not print `true`, skip the commit in this workspace.

### Task 4: Implement Learning Drawer State, Rendering, And Progress Feedback

**Files:**
- Modify: `static/realtime/app.js`
- Test: `tests/test_realtime_frontend.py`

- [ ] **Step 1: Extend state and element bindings**

Add these state fields near the top:

```javascript
  learningCardsCatalog: [],
  selectedLearningNodeId: null,
  learningCardsAvailable: false,
```

Replace the old `learningPathList` binding with the new drawer elements:

```javascript
  learningPathPanel: document.getElementById("learningPathPanel"),
  learningPathSummary: document.getElementById("learningPathSummary"),
  learningPathRecommended: document.getElementById("learningPathRecommended"),
  learningPathNodes: document.getElementById("learningPathNodes"),
  learningPathDetail: document.getElementById("learningPathDetail"),
  learningPathStatus: document.getElementById("learningPathStatus"),
```

- [ ] **Step 2: Add the learning-path helper constants and selectors**

Insert these helpers after the nav helpers:

```javascript
const learningTopicSummaries = {
  four_lessons: "先看四课结构，理解课体骨架。",
  three_transmissions: "理解事情从起因到收束的推进路径。",
  nine_rules: "研究九宗门的取传路径，当前仅作研究参考。",
  generals: "把天将当作象征角色来读，不当成现实承诺。",
  shensha: "识别神煞辅助标签，只作次级提示。",
  classical_symbols: "把经典象征和问题类别连起来读。",
  safety_boundary: "先学哪些问题不能直接下现实结论。",
  report_export: "了解本地分享和报告草稿的边界。",
};

const learningStatusLabels = {
  approved_for_mvp: "可学",
  research_only: "研究中",
};

function learningStatusClass(reviewStatus) {
  return reviewStatus === "approved_for_mvp" ? "available" : "research";
}

function summarizeLearningNode(node) {
  return learningTopicSummaries[node.topic] || "从这节开始建立稳定的解读视角。";
}

function learningCardsForNode(node) {
  const cardIds = new Set(node.learning_card_ids || []);
  return state.learningCardsCatalog.filter((card) => cardIds.has(card.card_id));
}

function recommendedLearningNode(nodes) {
  return (nodes || []).find((node) => node.review_status === "approved_for_mvp") || (nodes || [])[0] || null;
}

function selectedLearningNode(nodes) {
  if (!state.selectedLearningNodeId) {
    return recommendedLearningNode(nodes);
  }
  return (nodes || []).find((node) => node.node_id === state.selectedLearningNodeId) || recommendedLearningNode(nodes);
}
```

- [ ] **Step 3: Replace `loadLearningPath()` with path-plus-cards loading and render calls**

Replace the current function with:

```javascript
async function loadLearningPath() {
  if (!els.learningPathNodes || !els.learningPathSummary || !els.learningPathDetail) {
    return;
  }

  els.learningPathSummary.textContent = "学习路径加载中。";
  els.learningPathRecommended.innerHTML = '<p class="muted">推荐学习项加载中。</p>';
  els.learningPathNodes.innerHTML = "";
  els.learningPathDetail.innerHTML = '<p class="muted">选择一个节点查看详情。</p>';
  els.learningPathStatus.textContent = "";

  try {
    const [pathResponse, cardsResponse] = await Promise.all([
      fetch("/api/learning/path"),
      fetch("/api/learning/cards"),
    ]);

    if (!pathResponse.ok) {
      throw new Error(`Learning path failed: ${pathResponse.status}`);
    }

    state.learningPath = await pathResponse.json();
    if (cardsResponse.ok) {
      const cardsPayload = await cardsResponse.json();
      state.learningCardsCatalog = cardsPayload.learning_cards || [];
      state.learningCardsAvailable = true;
    } else {
      state.learningCardsCatalog = [];
      state.learningCardsAvailable = false;
      writeLog(els.toolLog, `Learning cards failed: ${cardsResponse.status}`);
    }

    renderLearningPathDrawer();
  } catch (error) {
    state.learningPath = null;
    state.learningCardsCatalog = [];
    state.learningCardsAvailable = false;
    els.learningPathSummary.textContent = "学习路径暂不可用";
    els.learningPathRecommended.innerHTML = '<p class="muted">推荐学习项暂不可用。</p>';
    els.learningPathNodes.innerHTML = "";
    els.learningPathDetail.innerHTML = '<p class="muted">请稍后重试。</p>';
    els.learningPathStatus.textContent = "学习路径暂不可用";
    writeLog(els.toolLog, error.message);
  }
}
```

- [ ] **Step 4: Add the drawer renderers**

Add these functions below `loadLearningPath()`:

```javascript
function renderLearningPathDrawer() {
  const nodes = state.learningPath?.nodes || [];
  const selectedNode = selectedLearningNode(nodes);
  const availableCount = nodes.filter((node) => node.review_status === "approved_for_mvp").length;
  const researchCount = nodes.filter((node) => node.review_status === "research_only").length;

  els.learningPathSummary.textContent = `共 ${nodes.length} 个节点，可学 ${availableCount} 个，研究中 ${researchCount} 个。`;
  renderLearningRecommendation(selectedNode);
  renderLearningNodes(nodes, selectedNode?.node_id || null);
  renderLearningDetail(selectedNode);
}

function renderLearningRecommendation(node) {
  if (!node) {
    els.learningPathRecommended.innerHTML = '<p class="muted">暂无推荐学习项。</p>';
    return;
  }
  const statusLabel = learningStatusLabels[node.review_status] || "未分类";
  const statusClass = learningStatusClass(node.review_status);
  const buttonText = node.review_status === "approved_for_mvp" ? "开始学习" : "暂不可学";
  const disabled = node.review_status === "approved_for_mvp" ? "" : "disabled";
  els.learningPathRecommended.innerHTML = `
    <p class="eyebrow">推荐下一步</p>
    <h2>${escapeHtml(node.title)}</h2>
    <p>${escapeHtml(summarizeLearningNode(node))}</p>
    <div class="learning-path-meta">
      <span class="status-pill ${statusClass}">${escapeHtml(statusLabel)}</span>
      <small>学习卡 ${escapeHtml((node.learning_card_ids || []).length)}</small>
      <small>出处 ${escapeHtml((node.source_ids || []).length)}</small>
      <small>示例 ${escapeHtml((node.example_case_ids || []).length)}</small>
    </div>
    <div class="learning-path-actions">
      <button type="button" data-action="start-learning" data-node-id="${escapeHtml(node.node_id)}" ${disabled}>${buttonText}</button>
    </div>
  `;
}

function renderLearningNodes(nodes, selectedNodeId) {
  els.learningPathNodes.innerHTML = nodes.map((node) => {
    const statusLabel = learningStatusLabels[node.review_status] || "未分类";
    const selected = node.node_id === selectedNodeId ? 'data-selected="true" aria-pressed="true"' : 'aria-pressed="false"';
    return `
      <button type="button" class="learning-path-node" data-node-id="${escapeHtml(node.node_id)}" ${selected}>
        <strong>${escapeHtml(node.title)}</strong>
        <p>${escapeHtml(summarizeLearningNode(node))}</p>
        <div class="learning-path-meta">
          <span class="status-pill ${learningStatusClass(node.review_status)}">${escapeHtml(statusLabel)}</span>
          <small>学习卡 ${escapeHtml((node.learning_card_ids || []).length)}</small>
          <small>出处 ${escapeHtml((node.source_ids || []).length)}</small>
          <small>示例 ${escapeHtml((node.example_case_ids || []).length)}</small>
        </div>
      </button>
    `;
  }).join("");
}

function renderLearningDetail(node) {
  if (!node) {
    els.learningPathDetail.innerHTML = '<p class="muted">选择一个节点查看详情。</p>';
    return;
  }
  const cards = learningCardsForNode(node);
  const statusLabel = learningStatusLabels[node.review_status] || "未分类";
  const readOnlyNote = node.review_status === "research_only"
    ? '<p class="muted">当前仅供研究参考，暂不作为公开学习节点。</p>'
    : "";
  const cardHtml = state.learningCardsAvailable
    ? (cards.length
      ? cards.map((card) => `<section class="mini"><strong>${escapeHtml(card.title)}</strong><p>${escapeHtml(card.summary)}</p></section>`).join("")
      : '<p class="muted">当前节点暂无关联学习卡。</p>')
    : '<p class="muted">关联学习卡暂不可用。</p>';
  const actionButton = node.review_status === "approved_for_mvp"
    ? `<button type="button" data-action="mark-read" data-node-id="${escapeHtml(node.node_id)}">标记已读</button>`
    : `<button type="button" data-action="mark-read" data-node-id="${escapeHtml(node.node_id)}" disabled>暂不可学</button>`;

  els.learningPathDetail.innerHTML = `
    <p class="eyebrow">节点详情</p>
    <h2>${escapeHtml(node.title)}</h2>
    <p>${escapeHtml(summarizeLearningNode(node))}</p>
    <div class="learning-path-meta">
      <span class="status-pill ${learningStatusClass(node.review_status)}">${escapeHtml(statusLabel)}</span>
      <small>解锁输出：${escapeHtml((node.unlocked_outputs || []).join("、") || "无")}</small>
      <small>出处：${escapeHtml((node.source_ids || []).join("、") || "无")}</small>
    </div>
    ${readOnlyNote}
    <div class="stack">${cardHtml}</div>
    <div class="learning-path-actions">${actionButton}</div>
  `;
}
```

- [ ] **Step 5: Add event wiring and progress feedback**

Bind both the node list and drawer action area:

```javascript
async function recordLearningDrawerProgress(nodeId, eventType, status) {
  const payload = {
    visitor_id: els.testerId.value.trim() || "anonymous",
    node_id: nodeId,
    event_type: eventType,
    status,
    mode: els.modeSelect.value,
    source: "realtime_frontend",
  };
  const response = await fetch("/api/learning/progress", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Learning progress failed: ${response.status}`);
  }
  return response.json();
}

function selectLearningNode(nodeId) {
  state.selectedLearningNodeId = nodeId;
  renderLearningPathDrawer();
}

if (els.learningPathNodes) {
  els.learningPathNodes.addEventListener("click", (event) => {
    const button = event.target.closest("[data-node-id]");
    if (!button) {
      return;
    }
    selectLearningNode(button.dataset.nodeId);
  });
}

if (els.learningPathRecommended) {
  els.learningPathRecommended.addEventListener("click", async (event) => {
    const button = event.target.closest('[data-action="start-learning"]');
    if (!button || button.disabled) {
      return;
    }
    selectLearningNode(button.dataset.nodeId);
    try {
      const result = await recordLearningDrawerProgress(button.dataset.nodeId, "learning_progress", "started");
      els.learningPathStatus.textContent = result.stored ? "学习进度已记录。" : "当前不保存进度，不影响浏览。";
    } catch (error) {
      els.learningPathStatus.textContent = "学习进度记录失败。";
      writeLog(els.toolLog, error.message);
    }
  });
}

if (els.learningPathDetail) {
  els.learningPathDetail.addEventListener("click", async (event) => {
    const button = event.target.closest('[data-action="mark-read"]');
    if (!button || button.disabled) {
      return;
    }
    try {
      const result = await recordLearningDrawerProgress(button.dataset.nodeId, "learning_progress", "completed");
      els.learningPathStatus.textContent = result.stored ? "已标记已读。" : "当前不保存进度，不影响浏览。";
    } catch (error) {
      els.learningPathStatus.textContent = "学习进度记录失败。";
      writeLog(els.toolLog, error.message);
    }
  });
}
```

- [ ] **Step 6: Remove the temporary `learningPathList` compatibility element and references**

Delete the old binding and any remaining usage:

```javascript
  learningPathList: document.getElementById("learningPathList"),
```

Remove any leftover `els.learningPathList.innerHTML = ...` logic and confirm the drawer now renders entirely through the new elements.

- [ ] **Step 7: Run the learning drawer tests and verify they pass**

Run:

```bash
python -m pytest tests/test_realtime_frontend.py -k "learning_path" -v
```

Expected: `PASS`

- [ ] **Step 8: Run the full frontend contract suite and JS syntax check**

Run:

```bash
python -m pytest tests/test_realtime_frontend.py -v
node --check static/realtime/app.js
```

Expected:

- `tests/test_realtime_frontend.py`: all tests pass
- `node --check`: exit code `0`

- [ ] **Step 9: Commit the JS implementation if git is available**

Run:

```bash
git rev-parse --is-inside-work-tree
```

If the command prints `true`, then run:

```bash
git add static/realtime/app.js static/realtime/index.html static/realtime/styles.css tests/test_realtime_frontend.py
git commit -m "feat: add interactive learning drawer"
```

If the command errors or does not print `true`, skip the commit in this workspace.

### Task 5: Final Verification And Spec Coverage Check

**Files:**
- Review: `docs/superpowers/specs/2026-05-10-liuren-learning-drawer-design.md`
- Review: `static/realtime/index.html`
- Review: `static/realtime/styles.css`
- Review: `static/realtime/app.js`
- Review: `tests/test_realtime_frontend.py`

- [ ] **Step 1: Re-read the spec and map each requirement to the shipped code**

Confirm these spec points are visible in code:

```text
- right-rail drawer placement
- recommendation card
- full node list
- detail area
- research-only disabled action
- learning cards fallback state
- no new route
- no new backend endpoint
```

- [ ] **Step 2: Run the exact final verification commands**

Run:

```bash
python -m pytest tests/test_realtime_frontend.py -v
python -m pytest tests/test_phase13_productization.py -k "frontend_and_schema_contracts_exist or phase13_api_contract_and_productization_gate" -v
node --check static/realtime/app.js
```

Expected:

- `tests/test_realtime_frontend.py`: all pass
- selected `phase13` contracts: pass, proving no API contract regression around learning path/productization
- `node --check`: exit code `0`

- [ ] **Step 3: Capture any non-goals or residual risks in the worker handoff**

Use this exact note if the implementation matches the spec:

```text
Residual risks:
- node summaries are still front-end mapped text, not backend-authored descriptions
- progress recording may remain non-persistent when productization gate is blocked
```

- [ ] **Step 4: Commit the final verification touch-up if git is available**

Run:

```bash
git rev-parse --is-inside-work-tree
```

If the command prints `true`, then run:

```bash
git add static/realtime/index.html static/realtime/styles.css static/realtime/app.js tests/test_realtime_frontend.py
git commit -m "test: verify learning drawer contract"
```

If the command errors or does not print `true`, skip the commit in this workspace.

## Self-Review

### Spec Coverage

- Drawer moved into `supportPanel`: covered by Task 1 static contract + Task 2 HTML move.
- Recommended next step: covered by Task 1 harness + Task 4 recommendation renderer.
- Full clickable node list: covered by Task 1 harness + Task 4 node renderer.
- In-drawer detail view: covered by Task 1 harness + Task 4 detail renderer.
- Research-only read-only state: covered by Task 1 harness + Task 4 disabled action logic.
- Degraded learning-card fetch behavior: covered by Task 1 harness + Task 4 `cardsResponse.ok` branch.
- No new route/backend: enforced in File Map and Task 5 coverage review.

### Placeholder Scan

- No `TODO`, `TBD`, or “implement later” placeholders remain.
- Every test/run/implementation step includes concrete file paths, commands, and code snippets.

### Type Consistency

- The plan consistently uses `learningPathPanel`, `learningPathSummary`, `learningPathRecommended`, `learningPathNodes`, `learningPathDetail`, and `learningPathStatus`.
- The plan consistently uses `approved_for_mvp` and `research_only` as the only status labels.
- The plan consistently treats `/api/learning/cards` as returning `{ "learning_cards": [...] }`.
