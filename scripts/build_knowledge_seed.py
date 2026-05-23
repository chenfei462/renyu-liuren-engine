from __future__ import annotations

from pathlib import Path

from liuren_engine.knowledge import write_source_cards_seed


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    target = write_source_cards_seed(root)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
