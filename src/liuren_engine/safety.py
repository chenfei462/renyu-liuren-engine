from __future__ import annotations

from .constants import CATEGORY_CLASSIC_SYMBOLS, HIGH_RISK_CATEGORIES


DISCLAIMER = "本产品为传统文化学习与娱乐体验，不构成医疗、法律、投资、职业、婚姻或安全决策建议。"

HIGH_RISK_CATEGORY_KEYWORDS = {
    "Q-009": (
        "\u533b\u7597",
        "\u5065\u5eb7",
        "\u75be\u75c5",
        "\u786e\u8bca",
        "\u7528\u836f",
    ),
    "Q-010": (
        "\u6cd5\u5f8b",
        "\u8bc9\u8bbc",
        "\u5408\u540c\u7ea0\u7eb7",
        "\u5f8b\u5e08",
    ),
    "Q-011": (
        "\u6295\u8d44",
        "\u80a1\u7968",
        "\u57fa\u91d1",
        "\u7406\u8d22",
        "\u4e70\u80a1",
        "\u5e01",
    ),
    "Q-012": (
        "\u4eba\u8eab\u5b89\u5168",
        "\u81ea\u4f24",
        "\u81ea\u6740",
        "\u5a01\u80c1",
        "\u5371\u9669",
    ),
}

LOW_RISK_CATEGORY_KEYWORDS = {
    "Q-001": (
        "\u5408\u4f5c",
        "\u63a8\u8fdb",
        "\u5bf9\u63a5",
        "\u8c08\u6210",
        "\u8c0b\u671b",
    ),
    "Q-002": (
        "\u611f\u60c5",
        "\u5173\u7cfb",
        "\u590d\u5408",
        "\u76f8\u5904",
        "\u8054\u7cfb",
    ),
    "Q-004": (
        "\u6c9f\u901a",
        "\u6d88\u606f",
        "\u6587\u4e66",
        "\u5b66\u4e60",
        "\u8003\u8bd5",
        "\u9762\u8bd5",
        "\u51fa\u884c",
    ),
    "Q-005": (
        "\u5de5\u4f5c",
        "\u6c42\u804c",
        "\u804c\u573a",
        "offer",
        "\u5165\u804c",
        "\u5c97\u4f4d",
        "\u673a\u4f1a",
        "\u53d1\u5c55",
    ),
}


def _matched_category(
    text: str, keyword_map: dict[str, tuple[str, ...]]
) -> str | None:
    normalized_text = text.casefold()
    for code, keywords in keyword_map.items():
        if any(keyword.casefold() in normalized_text for keyword in keywords):
            return code
    return None


def normalize_category(category: str | None, question: str | None = None) -> str | None:
    raw_category = category.strip() if isinstance(category, str) else ""
    question_text = str(question or "").strip()
    text = f"{raw_category} {question_text}"
    if raw_category in HIGH_RISK_CATEGORIES:
        return raw_category
    matched_high_risk = _matched_category(text, HIGH_RISK_CATEGORY_KEYWORDS)
    if matched_high_risk:
        return matched_high_risk
    if raw_category:
        return raw_category
    return _matched_category(question_text, LOW_RISK_CATEGORY_KEYWORDS)


def build_safety(category: str | None, question: str | None = None) -> dict:
    normalized_category = normalize_category(category, question)
    if normalized_category in HIGH_RISK_CATEGORIES:
        return {
            "is_high_risk": True,
            "category": normalized_category,
            "risk_type": HIGH_RISK_CATEGORIES[normalized_category],
            "action": "safety_only",
            "disclaimer": DISCLAIMER,
        }
    return {
        "is_high_risk": False,
        "category": normalized_category,
        "risk_type": None,
        "action": "allow_cultural_interpretation",
        "disclaimer": DISCLAIMER,
    }


def category_symbols(category: str | None, question: str | None = None) -> list[str]:
    return CATEGORY_CLASSIC_SYMBOLS.get(normalize_category(category, question) or "", [])
