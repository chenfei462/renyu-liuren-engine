# LiuRen App UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign `/app` as an "案牍工作台" realtime interpretation workspace while preserving the existing frontend JavaScript contract.

**Architecture:** Keep the static app architecture intact: `index.html` owns semantic layout and stable DOM ids, `styles.css` owns all visual treatment and responsive behavior, and `app.js` remains the business/runtime layer. The layout becomes top status/header, two-column workbench, and bottom secondary experiment panels.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, FastAPI static hosting, Python `unittest`/pytest frontend contract tests, Codex in-app browser verification.

---

## File Structure

- Modify `tests/test_realtime_frontend.py`: add structural contract checks for the new workbench layout, safety banner, primary/secondary hierarchy, and responsive CSS hooks.
- Modify `static/realtime/index.html`: restructure the page into topbar, main workbench, right assistant rail, and secondary panels while keeping all ids used by `app.js`.
- Replace `static/realtime/styles.css`: implement the warm paper visual system, two-column layout, stable controls, focus states, mobile ordering, and reduced-motion support.
- Do not modify `static/realtime/app.js` unless a test proves a DOM contract has changed. The implementation should preserve existing ids and class hooks.

## Task 1: Add Workbench Structure Tests

**Files:**
- Modify: `tests/test_realtime_frontend.py`
- Test: `tests/test_realtime_frontend.py`

- [ ] **Step 1: Add a failing test for the redesigned layout contract**

Append this method inside `RealtimeFrontendContractTests` after `test_static_realtime_page_has_expected_elements`:

```python
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
            ".secondary-grid",
            "@media (max-width: 900px)",
            "focus-visible",
            "prefers-reduced-motion",
        ]:
            self.assertIn(rule, css)
```

- [ ] **Step 2: Run the new test and verify it fails**

Run:

```powershell
python -m pytest tests/test_realtime_frontend.py::RealtimeFrontendContractTests::test_static_realtime_page_uses_workbench_layout -q
```

Expected: FAIL because the current HTML still uses `shell`, `toolbar`, and `grid`, and does not contain the new workbench classes.

## Task 2: Rebuild Static HTML Layout

**Files:**
- Modify: `static/realtime/index.html`
- Test: `tests/test_realtime_frontend.py`

- [ ] **Step 1: Replace the body markup with the workbench layout**

Keep the existing `<head>` and script path, then replace only the `<body>` content with this structure. Preserve all existing ids:

```html
  <body>
    <main class="app-shell">
      <header class="app-topbar">
        <div>
          <p class="eyebrow">受限 MVP</p>
          <h1 class="brand-mark">澹语 · 大六壬</h1>
        </div>
        <nav class="app-nav" aria-label="应用导航">
          <a href="#questionPanel" aria-current="page">起课</a>
          <a href="#learningMaterials">学习材料</a>
          <a href="#supportPanel">反馈</a>
          <a href="#experimentsPanel">沙箱</a>
        </nav>
        <div class="status-card" aria-live="polite">
          <span>当前状态</span>
          <strong id="status" class="status">idle</strong>
        </div>
      </header>

      <section class="safety-banner" aria-label="安全边界">
        <div>
          <strong>文化学习体验，不构成现实建议。</strong>
          <span>公开体验不保存录音；反馈、课式和删除请求仅用于产品复盘。</span>
        </div>
        <div class="legal-links" aria-label="MVP 范围说明">
          <a href="/">发布入口</a>
          <a href="/api/legal/privacy">隐私政策</a>
          <a href="/api/legal/safety">安全边界</a>
          <a href="/api/legal/copyright">版权说明</a>
        </div>
      </section>

      <section id="betaNotice" class="notice compact-notice">受限 Beta：传统文化学习与娱乐体验，不构成现实建议。</section>
      <section id="opsPauseNotice" class="notice compact-notice hidden">当前运维状态暂停讲盘，仅提供安全说明与反馈入口。</section>
      <section id="publicFeedbackNotice" class="notice compact-notice">公开 MVP 状态读取中。公开体验不保存录音；反馈、课式和删除请求仅用于产品复盘。</section>

      <section class="workbench">
        <div class="primary-column">
          <section id="questionPanel" class="panel question-panel" aria-label="text interpretation">
            <div class="section-heading">
              <p class="eyebrow">本次占问</p>
              <h2>输入一个具体事项</h2>
              <p>例如出行、合作、学习安排等；不回答天气、新闻、百科、计算或闲聊问题。</p>
            </div>
            <label for="textQuestion">文字起课 <span class="muted">只用于具体事项占问</span></label>
            <textarea id="textQuestion" placeholder="例如：明天出行是否顺利？这个合作能不能推进？"></textarea>
            <div class="control-grid">
              <label class="mode-control" for="modeSelect">
                解读口吻
                <select id="modeSelect">
                  <option value="professional">专业</option>
                  <option value="plain" selected>白话</option>
                  <option value="story">故事</option>
                  <option value="mentor">导师</option>
                </select>
              </label>
              <div class="voice-controls" aria-label="voice controls">
                <button id="connectBtn" type="button">连接</button>
                <button id="disconnectBtn" type="button" disabled>断开</button>
                <button id="interruptBtn" type="button" disabled>打断</button>
              </div>
              <button id="runTextInterpretBtn" class="primary-action" type="button">开始起课</button>
            </div>
            <p id="textInterpretStatus" class="form-status muted">不回答天气、新闻、百科、计算或闲聊问题。</p>
          </section>

          <article id="resultPanel" class="panel result-card">
            <div class="section-heading result-heading">
              <div>
                <p class="eyebrow">解读结果</p>
                <h2>先读结论，再看依据</h2>
              </div>
              <span class="state-pill">安全边界优先</span>
            </div>
            <div id="explainResult" class="readable-result">
              <p class="muted">输入问题后，这里会显示可直接阅读的解释。</p>
            </div>
            <p id="transcript" class="log hidden"></p>
          </article>
        </div>

        <aside id="supportPanel" class="assistant-rail" aria-label="辅助信息">
          <section class="panel rail-card" id="visitorProfilePanel">
            <p class="eyebrow">本地偏好</p>
            <label class="mode-control" for="visitorNickname">
              本地昵称
              <input id="visitorNickname" type="text" aria-label="本地访客昵称" />
            </label>
            <button id="saveVisitorProfileBtn" type="button">保存本地访客偏好</button>
            <span id="visitorProfileStatus" class="muted"></span>
          </section>

          <section class="panel rail-card">
            <p class="eyebrow">测试访问</p>
            <label class="mode-control" for="testerId">
              测试编号
              <input id="testerId" type="text" aria-label="测试用户编号" />
            </label>
            <label class="mode-control" for="inviteCode">
              邀请码
              <input id="inviteCode" type="text" aria-label="canary 邀请码" />
            </label>
          </section>

          <section class="panel rail-card">
            <p class="eyebrow">安全状态</p>
            <p id="safetyState" class="log compact">等待起课结果。</p>
          </section>

          <details id="learningMaterials" class="panel rail-card learning-panel">
            <summary>学习资料</summary>
            <p class="muted">学习资料会在生成解释后显示，不代表已经为当前问题起课。</p>
            <article>
              <h2>天将角色卡</h2>
              <div id="personaCards" class="stack"></div>
              <button id="personaCardsToggle" class="persona-toggle hidden" type="button">展开全部</button>
            </article>
            <article>
              <h2>学习卡</h2>
              <div id="learningCards" class="stack"></div>
            </article>
          </details>

          <section class="panel rail-card">
            <p class="eyebrow">反馈</p>
            <div class="feedback-grid">
              <label for="feedbackType">类型</label>
              <select id="feedbackType">
                <option value="helpful">有帮助</option>
                <option value="confusing">看不懂</option>
                <option value="source_insufficient">出处不足</option>
                <option value="safety_issue">安全问题</option>
                <option value="chart_question">排盘疑问</option>
                <option value="voice_issue">语音体验问题</option>
              </select>
              <label for="feedbackNote">备注</label>
              <textarea id="feedbackNote" aria-label="反馈备注"></textarea>
              <button id="submitFeedbackBtn" type="button">提交反馈</button>
              <p id="feedbackStatus" class="muted"></p>
            </div>
          </section>
        </aside>
      </section>

      <section id="experimentsPanel" class="secondary-grid" aria-label="次级实验区">
        <!-- Move the existing learning path, canary, monetization, B2B, membership, sandbox payment, debug, and share report panels here. -->
      </section>

      <audio id="remoteAudio" autoplay></audio>
    </main>
    <script src="/static/realtime/app.js?v=workbench-ui-1"></script>
  </body>
```

Then move these existing panels into `#experimentsPanel` without changing their ids: `learningPathPanel`, `canaryTaskList` article, `commercialInterest`, `monetizationPanel`, `businessLeadPanel`, `membershipTiersPanel`, `sandboxPaymentPanel`, `debugDetails`, and `shareReport`.

- [ ] **Step 2: Run frontend contract tests and fix missing ids**

Run:

```powershell
python -m pytest tests/test_realtime_frontend.py -q
```

Expected after fixes: all tests in `test_realtime_frontend.py` pass.

## Task 3: Implement Workbench CSS

**Files:**
- Replace: `static/realtime/styles.css`
- Test: `tests/test_realtime_frontend.py`

- [ ] **Step 1: Replace the old utilitarian CSS with the warm workbench design**

Use CSS variables for the design tokens and implement:

```css
:root {
  color-scheme: light;
  --ink: #111827;
  --muted: #5f6b7a;
  --faint: #8a94a3;
  --paper: #f7f3ea;
  --panel: #fffefa;
  --panel-soft: #fbf7ef;
  --line: #ddd2c0;
  --line-strong: #cfc0ab;
  --blue: #1e3a8a;
  --blue-dark: #10245d;
  --gold: #b7791f;
  --gold-soft: #fff3d5;
  --risk: #9f2f2f;
  --shadow: 0 24px 70px rgba(17, 24, 39, 0.12);
  background: var(--paper);
  color: var(--ink);
  font-family: "Noto Sans SC", "Microsoft YaHei", "PingFang SC", sans-serif;
}

body {
  margin: 0;
  min-width: 320px;
  background:
    linear-gradient(120deg, rgba(30, 58, 138, 0.07), transparent 38%),
    radial-gradient(circle at 88% 0%, rgba(183, 121, 31, 0.12), transparent 28%),
    var(--paper);
}

.app-shell {
  width: min(1440px, calc(100% - 40px));
  margin: 0 auto;
  padding: 24px 0 36px;
}

.app-topbar,
.safety-banner,
.workbench,
.secondary-grid {
  width: 100%;
}
```

Continue with explicit rules for `.app-topbar`, `.brand-mark`, `.app-nav`, `.status-card`, `.safety-banner`, `.panel`, `.workbench`, `.primary-column`, `.assistant-rail`, `.secondary-grid`, `.question-panel`, `.result-card`, `.readable-result`, `.voice-controls`, `.primary-action`, `.notice`, `.hidden`, `.persona-toggle`, `.debug-details`, `.feedback-grid`, and mobile media queries.

- [ ] **Step 2: Include accessibility and responsive hooks**

Ensure the CSS contains these exact hooks:

```css
button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
summary:focus-visible {
  outline: 3px solid rgba(30, 58, 138, 0.28);
  outline-offset: 2px;
}

@media (max-width: 900px) {
  .workbench,
  .secondary-grid {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}
```

- [ ] **Step 3: Run the structural frontend tests**

Run:

```powershell
python -m pytest tests/test_realtime_frontend.py -q
```

Expected: PASS.

## Task 4: Browser Verification

**Files:**
- Verify: `static/realtime/index.html`
- Verify: `static/realtime/styles.css`

- [ ] **Step 1: Start or reuse the FastAPI app**

Run:

```powershell
python -m uvicorn liuren_engine.webapp:app --host 127.0.0.1 --port 8003
```

Expected: server starts and serves `/app`.

- [ ] **Step 2: Open `/app` in the Codex in-app browser**

Navigate to:

```text
http://127.0.0.1:8003/app
```

Expected: the first viewport shows the topbar, safety banner, question panel, result panel, and right assistant rail. Commercialization and sandbox panels are below the main workbench.

- [ ] **Step 3: Check responsive breakpoints**

Use browser viewport checks at 1440px, 1024px, 768px, and 375px.

Expected:

- No text overlaps.
- Main CTA remains visible near the question panel.
- At mobile width, order is header, safety banner, question panel, result panel, assistant rail, secondary experiments.
- Focus states are visible when tabbing through links, inputs, selects, and buttons.

## Task 5: Full Verification

**Files:**
- Verify: entire repo

- [ ] **Step 1: Run the focused frontend tests**

Run:

```powershell
python -m pytest tests/test_realtime_frontend.py -q
```

Expected: PASS.

- [ ] **Step 2: Run the project test suite**

Run:

```powershell
python -m pytest -q
```

Expected: PASS, or report exact failing tests with stdout/stderr if failures are unrelated or pre-existing.

- [ ] **Step 3: Report changed files and verification**

Report:

- `tests/test_realtime_frontend.py`
- `static/realtime/index.html`
- `static/realtime/styles.css`
- Any `app.js` change if it became necessary

Also report each verification command and its result.
