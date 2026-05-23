# Persona Cards Expand Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an expand/collapse control to the realtime persona cards panel so users see 4 cards by default and can reveal all returned cards on demand.

**Architecture:** Keep the backend response unchanged and implement the feature entirely in the realtime frontend. Add a dedicated toggle button in the learning materials markup, store the current persona card list plus expanded/collapsed UI state in `app.js`, and render either the first 4 cards or the full list based on that state. Use a small CSS rule set so the toggle looks native to the existing page without changing the broader layout.

**Tech Stack:** Static HTML, vanilla JavaScript, CSS, Python `unittest` executed through `pytest`

---

## File Structure

- Modify: `D:\Desktop\六壬\static\realtime\index.html`
  Add a hidden toggle button immediately below `#personaCards` so the UI has a stable element for expand/collapse control.
- Modify: `D:\Desktop\六壬\static\realtime\app.js`
  Add persona card UI state, toggle label logic, click handling, and reset-to-collapsed behavior when new interpretation results arrive.
- Modify: `D:\Desktop\六壬\static\realtime\styles.css`
  Add minimal layout styles for the persona toggle so it sits below the cards and aligns with the current visual system.
- Modify: `D:\Desktop\六壬\tests\test_realtime_frontend.py`
  Extend the frontend contract tests so they cover the new HTML id, the JS toggle state, and the default-to-4 rendering logic.

### Task 1: Add Contract Coverage For The Persona Toggle

**Files:**
- Modify: `D:\Desktop\六壬\tests\test_realtime_frontend.py`
- Test: `D:\Desktop\六壬\tests\test_realtime_frontend.py`

- [ ] **Step 1: Write the failing test**

```python
for element_id in [
    "learningMaterials",
    "personaCards",
    "personaCardsToggle",
    "learningCards",
    "shareReport",
]:
    self.assertIn(f'id="{element_id}"', html)

for snippet in [
    "personaCardsToggle",
    "personaCardsExpanded",
    "personaCardLines",
    "defaultPersonaCardCount = 4",
    "展开全部",
    "收起",
    "lines.slice(0, defaultPersonaCardCount)",
    "personaLines.length > defaultPersonaCardCount",
]:
    self.assertIn(snippet, js)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_frontend.py -q`

Expected: `FAIL` because `personaCardsToggle`, `personaCardsExpanded`, and the new toggle strings are not present yet.

- [ ] **Step 3: Write the minimal implementation to satisfy the new contract**

```html
<article>
  <h2>天将角色卡</h2>
  <div id="personaCards" class="stack"></div>
  <button id="personaCardsToggle" class="persona-toggle hidden" type="button">展开全部</button>
</article>
```

```javascript
const state = {
  pc: null,
  dc: null,
  stream: null,
  lastResponseItemId: null,
  lastToolResult: null,
  personaCardLines: [],
  personaCardsExpanded: false,
};

const els = {
  learningMaterials: document.getElementById("learningMaterials"),
  personaCards: document.getElementById("personaCards"),
  personaCardsToggle: document.getElementById("personaCardsToggle"),
};

const defaultPersonaCardCount = 4;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_frontend.py -q`

Expected: `PASS` with the frontend contract suite back to green.

- [ ] **Step 5: Record that Git commit is unavailable in this workspace**

Run: `git -C D:\Desktop\六壬 status --short`

Expected: `fatal: not a git repository (or any of the parent directories): .git`

### Task 2: Implement Expand/Collapse Rendering In The Browser Client

**Files:**
- Modify: `D:\Desktop\六壬\static\realtime\app.js`
- Test: `D:\Desktop\六壬\tests\test_realtime_frontend.py`

- [ ] **Step 1: Write the failing test for default-collapsed rendering and reset behavior**

```python
for snippet in [
    "state.personaCardLines = personaLines",
    "state.personaCardsExpanded = false",
    "const lines = state.personaCardLines || [];",
    "const visibleLines = state.personaCardsExpanded ? lines : lines.slice(0, defaultPersonaCardCount)",
    'els.personaCardsToggle.textContent = state.personaCardsExpanded ? "收起" : "展开全部"',
    "els.personaCardsToggle.classList.toggle(\"hidden\", lines.length <= defaultPersonaCardCount)",
    "els.personaCardsToggle.addEventListener(\"click\"",
]:
    self.assertIn(snippet, js)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_frontend.py -q`

Expected: `FAIL` because the browser client still renders every card directly and has no stored expand/collapse state.

- [ ] **Step 3: Write the minimal implementation**

```javascript
function renderPersonaLines() {
  const lines = state.personaCardLines || [];
  if (!lines.length) {
    els.personaCards.innerHTML = '<p class="muted">本次暂无角色化输出。</p>';
    els.personaCardsToggle.classList.add("hidden");
    els.personaCardsToggle.textContent = "展开全部";
    return;
  }

  const visibleLines = state.personaCardsExpanded
    ? lines
    : lines.slice(0, defaultPersonaCardCount);

  els.personaCards.innerHTML = visibleLines
    .map(
      (line) => `
        <section class="mini">
          <strong>${escapeHtml(line.general)} 路 ${escapeHtml(line.role_name)}</strong>
          <p>${escapeHtml(line.line)}</p>
          <small>${escapeHtml(line.safety_note)}</small>
        </section>
      `,
    )
    .join("");

  els.personaCardsToggle.classList.toggle("hidden", lines.length <= defaultPersonaCardCount);
  els.personaCardsToggle.textContent = state.personaCardsExpanded ? "收起" : "展开全部";
}

function renderEntertainment(result) {
  const entertainment = result.interpretation?.entertainment || {};
  const personaLines = entertainment.persona_lines || [];
  const learningCards = entertainment.learning_cards || [];
  const hasLearningMaterials = personaLines.length > 0 || learningCards.length > 0;

  state.personaCardLines = personaLines;
  state.personaCardsExpanded = false;

  renderPersonaLines();
  renderLearningCards(learningCards);
  renderShareReport(entertainment.share_report || {});
  if (els.learningMaterials) {
    els.learningMaterials.open = hasLearningMaterials;
  }
}

if (els.personaCardsToggle) {
  els.personaCardsToggle.addEventListener("click", () => {
    state.personaCardsExpanded = !state.personaCardsExpanded;
    renderPersonaLines();
  });
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_frontend.py -q`

Expected: `PASS` with all three frontend contract tests succeeding.

- [ ] **Step 5: Record that Git commit is unavailable in this workspace**

Run: `git -C D:\Desktop\六壬 status --short`

Expected: `fatal: not a git repository (or any of the parent directories): .git`

### Task 3: Style The Toggle And Run Final Verification

**Files:**
- Modify: `D:\Desktop\六壬\static\realtime\styles.css`
- Modify: `D:\Desktop\六壬\tests\test_realtime_frontend.py`
- Test: `D:\Desktop\六壬\tests\test_realtime_frontend.py`

- [ ] **Step 1: Write the failing test for the toggle style hook**

```python
css = (ROOT / "static" / "realtime" / "styles.css").read_text(encoding="utf-8")

for snippet in [
    ".persona-toggle",
    "margin-top: 12px",
    "display: inline-flex",
]:
    self.assertIn(snippet, css)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_frontend.py -q`

Expected: `FAIL` because the stylesheet does not yet define the persona toggle class.

- [ ] **Step 3: Write the minimal implementation**

```css
.persona-toggle {
  margin-top: 12px;
  display: inline-flex;
}
```

- [ ] **Step 4: Run the focused test suite and then the related service suite**

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_frontend.py -q`
Expected: `3 passed`.

Run: `python -m pytest D:\Desktop\六壬\tests\test_realtime_service.py -q`
Expected: `12 passed, 2 subtests passed` for the realtime service contract suite, confirming the frontend change did not break adjacent behavior assumptions.

- [ ] **Step 5: Record that Git commit is unavailable in this workspace**

Run: `git -C D:\Desktop\六壬 status --short`

Expected: `fatal: not a git repository (or any of the parent directories): .git`
