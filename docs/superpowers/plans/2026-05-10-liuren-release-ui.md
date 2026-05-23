# LiuRen Release UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the release homepage as a trust-focused entry page that explains the product, MVP scope, safety boundaries, current launch status, and routes users to `/app`.

**Architecture:** Keep the existing static release page and inline status-fetching script. `static/release/index.html` owns semantic sections and all ids consumed by existing tests and scripts; `static/release/styles.css` owns the warm paper visual system, product preview, responsive grids, and accessibility states.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript inline fetches, FastAPI static hosting, Python `unittest`/pytest contracts, Codex in-app browser verification.

---

## File Structure

- Modify `tests/test_phase8_release.py`: add a focused homepage structure test for trust-entry layout classes, CTA hierarchy, preview section, and accessibility CSS hooks.
- Modify `static/release/index.html`: restructure the page into top navigation, hero/trust cards, scope cards, launch-status cards, compliance cards, final CTA, preserving existing ids and inline fetch targets.
- Replace `static/release/styles.css`: implement the release-specific visual system consistent with `/app`.

## Task 1: Add Release Homepage Structure Test

**Files:**
- Modify: `tests/test_phase8_release.py`
- Test: `tests/test_phase8_release.py`

- [ ] **Step 1: Add the failing test**

Add this method after `test_release_homepage_links_to_app_and_legal_documents`:

```python
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
```

- [ ] **Step 2: Run the new test and verify it fails**

Run:

```powershell
python -m pytest tests/test_phase8_release.py::PhaseEightReleaseTests::test_release_homepage_uses_trust_entry_layout -q
```

Expected: FAIL because the current page still uses the old `release-shell` and simple `hero/panel/grid` layout.

## Task 2: Rebuild Release HTML

**Files:**
- Modify: `static/release/index.html`
- Test: `tests/test_phase8_release.py`

- [ ] **Step 1: Replace the static release markup**

Replace the visible body markup with these semantic sections while preserving all existing status ids: `releaseScope`, `opsStatus`, `canaryStatus`, `contentCalendar`, `phase11Canary`, `phase12Public`, `phase13Productization`, `phase14Monetization`, and `phase15Payment`.

Required structure:

```html
<main class="release-shell trust-entry">
  <nav class="release-nav" aria-label="发布页导航">...</nav>
  <section class="hero-grid">...</section>
  <section class="trust-strip">...</section>
  <section id="mvpScope" class="section-band">...</section>
  <section id="launchStatus" class="section-band">...</section>
  <section id="safetyBoundary" class="section-band">...</section>
  <section id="finalCta" class="final-cta">...</section>
</main>
```

The hero must include:

- `澹语 · 大六壬`
- `大六壬实时解读的文化学习入口`
- a primary `/app` link with text `进入 Web App`
- a secondary `/api/release/readiness` link with text `查看发布准入`
- a `.product-preview` card showing static text for `本次占问`, `解读结果`, and `安全边界优先`

- [ ] **Step 2: Keep inline fetch script ids intact**

Keep the current inline script fetches and ensure each `document.getElementById(...)` target still exists:

- `opsStatusText`
- `canaryStatusText`
- `contentCalendarList`
- `phase11CanaryText`
- `phase12PublicText`
- `phase13ProductizationText`
- `phase14MonetizationText`
- `phase15PaymentText`

- [ ] **Step 3: Run release tests and fix missing text or ids**

Run:

```powershell
python -m pytest tests/test_phase8_release.py tests/test_phase9_ops.py tests/test_phase10_growth.py tests/test_phase11_canary.py tests/test_phase12_public_launch.py tests/test_phase13_productization.py tests/test_phase14_monetization.py tests/test_phase15_payment.py -q
```

Expected after fixes: PASS.

## Task 3: Replace Release CSS

**Files:**
- Replace: `static/release/styles.css`
- Test: `tests/test_phase8_release.py`

- [ ] **Step 1: Implement the trust-entry visual system**

Use CSS variables for warm paper, ink, trust blue, gold, and risk colors. Implement rules for:

- `.release-shell`
- `.release-nav`
- `.hero-grid`
- `.product-preview`
- `.trust-strip`
- `.scope-grid`
- `.status-grid`
- `.legal-grid`
- `.final-cta`
- `.button.primary`
- `.status-panel`
- responsive media queries

- [ ] **Step 2: Include accessibility and reduced-motion hooks**

Ensure these exact strings exist in CSS:

```css
a:focus-visible,
button:focus-visible {
  outline: 3px solid rgba(30, 58, 138, 0.3);
  outline-offset: 3px;
}

@media (max-width: 900px) {
  .hero-grid,
  .trust-strip,
  .scope-grid,
  .status-grid,
  .legal-grid {
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

- [ ] **Step 3: Run the focused release test**

Run:

```powershell
python -m pytest tests/test_phase8_release.py -q
```

Expected: PASS.

## Task 4: Browser Verification

**Files:**
- Verify: `static/release/index.html`
- Verify: `static/release/styles.css`

- [ ] **Step 1: Reuse or start FastAPI app**

Run:

```powershell
$env:PYTHONPATH='D:\Desktop\六壬\src'; python -m uvicorn liuren_engine.webapp:app --host 127.0.0.1 --port 8003
```

Expected: `/` returns the release homepage.

- [ ] **Step 2: Open the release page**

Navigate the in-app browser to:

```text
http://127.0.0.1:8003/
```

Expected: first viewport shows brand, product positioning, `/app` CTA, readiness CTA, product preview, and trust cards.

- [ ] **Step 3: Check desktop and mobile widths**

Check 1440px and 375px.

Expected:

- no text overlap
- CTA buttons remain visible
- product preview follows hero copy on mobile
- status cards remain below MVP scope and not above the hero

## Task 5: Full Verification

**Files:**
- Verify: whole project

- [ ] **Step 1: Run release-focused tests**

Run:

```powershell
python -m pytest tests/test_phase8_release.py tests/test_phase9_ops.py tests/test_phase10_growth.py tests/test_phase11_canary.py tests/test_phase12_public_launch.py tests/test_phase13_productization.py tests/test_phase14_monetization.py tests/test_phase15_payment.py -q
```

Expected: PASS.

- [ ] **Step 2: Run all tests**

Run:

```powershell
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 3: Report changes and verification**

Report changed files:

- `tests/test_phase8_release.py`
- `static/release/index.html`
- `static/release/styles.css`
- `docs/superpowers/specs/2026-05-10-liuren-release-ui-design.md`
- `docs/superpowers/plans/2026-05-10-liuren-release-ui.md`

Report exact test commands and browser checks.
