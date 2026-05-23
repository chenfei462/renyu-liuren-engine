from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import create_liuren_chart


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Create a RenYu Da Liu Ren chart JSON payload.")
    parser.add_argument("--request", required=True, help="Path to request JSON file.")
    args = parser.parse_args(argv)

    request_path = Path(args.request)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    chart = create_liuren_chart(request)
    json.dump(chart, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
