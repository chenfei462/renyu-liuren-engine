from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


RULE_CARDS_PATH = Path("phase1_research") / "data" / "rule_source_cards.v0.1.md"
SOURCE_CARDS_SEED_PATH = Path("data") / "source_cards.v0.1.json"


def _split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _source_location_parts(location: str) -> tuple[str, str]:
    if " " in location:
        book, chapter = location.split(" ", 1)
        return book.strip(), chapter.strip()
    return location.strip(), ""


def _copyright_status(row: Mapping[str, str]) -> str:
    joined = " ".join(row.values())
    if "不摘正文" in joined or "未授权" in joined or "现代出版物" in joined:
        return "metadata_or_summary_only"
    if "不可上线正文" in joined:
        return "not_for_launch_body"
    return "summary_and_short_excerpt_only"


def _tags(row: Mapping[str, str]) -> list[str]:
    tags = [row["模块"], row["规则类型"], row["上线状态"]]
    summary_tokens = re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]{2,}", row["现代摘要或规则化转写"])
    for token in summary_tokens[:8]:
        if token not in tags:
            tags.append(token)
    return tags


def build_source_cards_from_phase1(root: str | Path) -> list[dict]:
    root_path = Path(root)
    rule_cards_path = root_path / RULE_CARDS_PATH
    lines = rule_cards_path.read_text(encoding="utf-8").splitlines()
    headers: list[str] | None = None
    cards: list[dict] = []
    for line in lines:
        if line.startswith("| card_id "):
            headers = _split_markdown_row(line)
            continue
        if not line.startswith("| RC-"):
            continue
        if headers is None:
            raise ValueError("rule source card header was not found")
        cells = _split_markdown_row(line)
        row = dict(zip(headers, cells))
        book, chapter = _source_location_parts(row["来源/定位"])
        cards.append(
            {
                "source_id": row["card_id"],
                "book_or_source": book,
                "chapter_or_location": chapter,
                "claim_type": row["依据类型"],
                "summary": row["现代摘要或规则化转写"],
                "module": row["模块"],
                "rule_type": row["规则类型"],
                "launch_status": row["上线状态"],
                "tags": _tags(row),
                "safety_note": row["风险说明"],
                "copyright_status": _copyright_status(row),
            }
        )
    return cards


def write_source_cards_seed(root: str | Path) -> Path:
    root_path = Path(root)
    cards = build_source_cards_from_phase1(root_path)
    target = root_path / SOURCE_CARDS_SEED_PATH
    target.write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def load_source_cards(root: str | Path | None = None) -> list[dict]:
    root_path = Path(root) if root is not None else Path.cwd()
    seed_path = root_path / SOURCE_CARDS_SEED_PATH
    if seed_path.exists():
        return json.loads(seed_path.read_text(encoding="utf-8"))
    return build_source_cards_from_phase1(root_path)


def _collect_exact_source_ids(chart_json: Mapping[str, Any]) -> list[str]:
    source_ids: list[str] = ["RC-008", "RC-009", "RC-010", "RC-013", "RC-014", "RC-015", "RC-067"]
    for transmission in chart_json.get("three_transmissions", []):
        source_ids.extend(transmission.get("source_cards", []))
    for candidate in chart_json.get("rule_trace", {}).get("transmission_candidates", []):
        if candidate.get("status") in {"matched", "requires_expert_review"}:
            source_ids.extend(candidate.get("source_cards", []))
    for shensha in chart_json.get("shensha", []):
        source_ids.extend(source_id for source_id in shensha.get("source_cards", []) if source_id.startswith("RC-"))
    if chart_json.get("safety", {}).get("is_high_risk"):
        source_ids.extend(["RC-102", "RC-103"])
    else:
        source_ids.append("RC-102")
    return list(dict.fromkeys(source_ids))


def _keywords(chart_json: Mapping[str, Any], query: str | None) -> list[str]:
    tokens: list[str] = []
    if query:
        tokens.extend(re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]{2,}", query))
    tokens.extend(str(item.get("lesson_type", "")) for item in chart_json.get("three_transmissions", []))
    tokens.extend(chart_json.get("rule_trace", {}).get("category_symbols", []))
    tokens.extend(str(item.get("general", "")) for item in chart_json.get("generals", [])[:4])
    tokens.extend(str(item.get("name", "")) for item in chart_json.get("shensha", []))
    risk_type = chart_json.get("safety", {}).get("risk_type")
    if risk_type:
        tokens.append(str(risk_type))
    return [token for token in dict.fromkeys(tokens) if token]


def _score(card: Mapping[str, Any], tokens: list[str]) -> int:
    text = " ".join(
        [
            str(card.get("source_id", "")),
            str(card.get("book_or_source", "")),
            str(card.get("chapter_or_location", "")),
            str(card.get("summary", "")),
            " ".join(card.get("tags", [])),
        ]
    )
    return sum(3 if token in str(card.get("source_id", "")) else 1 for token in tokens if token and token in text)


def retrieve_evidence(chart_json: Mapping[str, Any], query: str | None = None, mode: str = "professional") -> list[dict]:
    if not chart_json:
        raise ValueError("chart_json is required")
    root = Path(__file__).resolve().parents[2]
    cards = load_source_cards(root)
    by_id = {card["source_id"]: card for card in cards}

    selected: list[dict] = []
    for source_id in _collect_exact_source_ids(chart_json):
        card = by_id.get(source_id)
        if card and card not in selected:
            selected.append(card)

    tokens = _keywords(chart_json, query)
    scored = sorted(
        ((score, card) for card in cards if (score := _score(card, tokens)) > 0),
        key=lambda item: (-item[0], item[1]["source_id"]),
    )
    for _, card in scored:
        if card not in selected:
            selected.append(card)
        if len(selected) >= (16 if mode == "plain" else 24):
            break
    return selected
