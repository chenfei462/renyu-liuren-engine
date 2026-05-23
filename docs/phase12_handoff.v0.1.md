# Phase 12 Handoff v0.1

## Scope

Phase 12 adds the controlled public MVP layer. Public access is only allowed when `/api/public-release/gate` returns `ready_for_phase12`; otherwise `/api/public/status` stays `blocked`.

## Implemented Artifacts

- `data/public_launch_config.v0.1.json`
- `data/public_session_log.v0.1.jsonl`
- `data/public_incidents.v0.1.jsonl`
- `data/public_metrics.v0.1.json`
- `data/phase12_public_launch_report.v0.1.json`
- Public launch APIs under `/api/public/*`
- `/api/phase12/report`
- Public pause guard in `/api/liuren/interpret`
- Release and realtime frontend public status notices

## Launch Rules

- `blocked`: public release gate is not ready.
- `preview`: public release gate is ready and low-traffic validation can begin.
- `live`: manually promoted public MVP state.
- `paused`: P0/P1 public incident or manual public pause.

## Current Expected State

The current repository defaults to `blocked` because expert review and canary readiness gates are not yet cleared. Phase 12 must not bypass that gate.
