from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import create_liuren_chart
from .interpreter import generate_interpretation
from .knowledge import retrieve_evidence


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Create a chart and local evidence-backed interpretation.")
    parser.add_argument("--request", required=True, help="Path to request JSON file.")
    args = parser.parse_args(argv)

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    mode = request.get("mode", "professional")
    chart = request.get("chart_json") or create_liuren_chart(request)
    evidence = retrieve_evidence(chart, query=request.get("query") or request.get("question"), mode=mode)
    interpretation = generate_interpretation(chart, evidence, mode=mode)
    json.dump({"chart": chart, "evidence": evidence, "interpretation": interpretation}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
