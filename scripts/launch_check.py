from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liuren_engine.release import build_release_readiness, load_launch_checklist, load_release_config


FORBIDDEN_VISIBLE_TERMS = ["包赢", "必赚", "确诊", "用药", "胜诉", "准确率保证"]
VISIBLE_PATHS = [ROOT / "static"]
VISIBLE_FILES = [
    ROOT / "docs" / "privacy_policy.v0.1.md",
    ROOT / "docs" / "user_notice.v0.1.md",
    ROOT / "docs" / "safety_boundaries.v0.1.md",
    ROOT / "docs" / "copyright_notice.v0.1.md",
    ROOT / "docs" / "pricing_strategy.v0.1.md",
    ROOT / "docs" / "phase8_handoff.v0.1.md",
]


def scan_forbidden_terms() -> list[dict]:
    findings: list[dict] = []
    for base in VISIBLE_PATHS:
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in FORBIDDEN_VISIBLE_TERMS:
                if term in text:
                    findings.append({"path": str(path.relative_to(ROOT)), "term": term})
    for path in VISIBLE_FILES:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term in FORBIDDEN_VISIBLE_TERMS:
            if term in text:
                findings.append({"path": str(path.relative_to(ROOT)), "term": term})
    return findings


def main() -> int:
    config = load_release_config(ROOT)
    readiness = build_release_readiness(ROOT)
    checklist = load_launch_checklist(ROOT)
    forbidden_findings = scan_forbidden_terms()
    high_risk_open = sorted(set(config["allowed_categories"]) & {"Q-009", "Q-010", "Q-011", "Q-012"})
    report = {
        "checklist_id": checklist["checklist_id"],
        "release_id": config["release_id"],
        "release_status": readiness["release_status"],
        "blocked_reasons": readiness["blocked_reasons"],
        "high_risk_categories_open": high_risk_open,
        "forbidden_visible_terms": forbidden_findings,
        "passed": not high_risk_open and not forbidden_findings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
