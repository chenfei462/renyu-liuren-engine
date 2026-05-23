from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = ROOT / "static"
PUBLIC_STATIC_ROOT = ROOT / "public" / "static"


def main() -> int:
    if not STATIC_ROOT.exists():
        raise FileNotFoundError(f"static assets not found: {STATIC_ROOT}")
    if PUBLIC_STATIC_ROOT.exists():
        shutil.rmtree(PUBLIC_STATIC_ROOT)
    shutil.copytree(STATIC_ROOT, PUBLIC_STATIC_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

