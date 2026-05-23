# Phase 13 Handoff v0.1

## Scope

Phase 13 adds the first productization experiment layer. It does not bypass Phase 12: `/api/productization/gate` only enters `experiment` when public MVP status is `preview` or `live` and no public risk event is active.

## Implemented Artifacts

- `data/productization_config.v0.1.json`
- `data/productization_gate.v0.1.json`
- `data/visitor_profile.v0.1.jsonl`
- `data/learning_progress.v0.1.jsonl`
- `data/learning_path.v0.1.json`
- `data/product_metrics.v0.1.json`
- `data/phase13_productization_report.v0.1.json`
- Productization APIs under `/api/productization/*`, `/api/visitor/profile`, `/api/learning/*`, `/api/product/metrics`, and `/api/phase13/report`
- Local PDF report draft field in share report responses
- Release and realtime frontend productization panels

## Gate Rules

- `blocked`: public MVP is not `preview` or `live`, or productization is disabled.
- `experiment`: public MVP is active and no critical public incident is present.
- `paused`: public MVP is paused, or public metrics show a critical safety, evidence, copyright, or Realtime tool incident.

## Current Expected State

The current repository defaults to `blocked` because the Phase 12 public launch gate remains blocked. Phase 13 records are therefore guarded at the API layer until Phase 12 is ready.
