# Persona Cards Expand Design

## Goal

Adjust the realtime frontend persona cards panel so it shows 4 cards by default and lets the user expand to see all returned cards.

## Scope

- Frontend-only behavior change in `static/realtime/`.
- No backend API shape changes.
- No change to persona selection logic on the server.

## Current Behavior

- The backend currently returns up to 4 persona lines for the common fallback path.
- The frontend renders every persona line it receives with no expand/collapse control.

## Desired Behavior

- Keep the default collapsed presentation at 4 cards.
- If the frontend receives more than 4 persona lines, show a toggle control below the cards.
- The toggle label switches between `展开全部` and `收起`.
- Expanding reveals all returned persona cards for the current result only.
- When a new interpretation result is rendered, the persona cards reset to the collapsed state.
- If there are 4 or fewer persona lines, do not show the toggle.

## UI Notes

- The toggle should live inside the learning materials persona card area so it feels attached to that section.
- The control should be lightweight and match the existing static page style.
- Empty-state behavior stays unchanged.

## Data Flow

1. `renderEntertainment` receives `interpretation.entertainment.persona_lines`.
2. The frontend stores the current list plus an expanded/collapsed flag.
3. `renderPersonaLines` renders either the first 4 items or the full list depending on that flag.
4. Clicking the toggle flips the flag and re-renders the same list.
5. Rendering a new result replaces the stored list and resets the flag to collapsed.

## Testing

- Add a frontend contract test that checks for the new toggle wiring in `app.js`.
- Verify existing frontend contract tests still pass.

## Constraints

- Keep the implementation small and local to the realtime frontend.
- Do not change report generation, learning cards, or backend persona selection.

## Notes

- `D:\Desktop\六壬` is not currently a Git repository in this environment, so this design doc cannot be committed here.
