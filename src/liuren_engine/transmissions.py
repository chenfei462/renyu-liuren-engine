from __future__ import annotations

from .constants import BRANCHES
from .relations import opposite_branch


def _transmission_payload(
    branches: list[str],
    lesson_type: str,
    rule_id: str,
    source_cards: list[str],
    needs_expert_review: bool,
) -> list[dict]:
    labels = ["初传", "中传", "末传"]
    return [
        {
            "position": index + 1,
            "label": labels[index],
            "branch": branch,
            "lesson_type": lesson_type,
            "rule_id": rule_id,
            "source_cards": source_cards,
            "needs_expert_review": needs_expert_review,
        }
        for index, branch in enumerate(branches)
    ]


def _follow_sky(initial: str, sky: dict[str, str]) -> list[str]:
    middle = sky[initial]
    final = sky[middle]
    return [initial, middle, final]


def _is_fuyin(heaven_plate: list[dict]) -> bool:
    return all(item["earth_branch"] == item["heaven_branch"] for item in heaven_plate)


def _is_fanyin(heaven_plate: list[dict]) -> bool:
    return all(item["heaven_branch"] == opposite_branch(item["earth_branch"]) for item in heaven_plate)


def build_three_transmissions(four_lessons: list[dict], sky: dict[str, str], heaven_plate: list[dict], day_branch: str) -> tuple[list[dict], list[dict], str]:
    upper_controls = [lesson for lesson in four_lessons if lesson["relation"] == "upper_controls_lower"]
    lower_controls = [lesson for lesson in four_lessons if lesson["relation"] == "lower_controls_upper"]
    fuyin = _is_fuyin(heaven_plate)
    fanyin = _is_fanyin(heaven_plate)

    candidates = [
        {
            "rule_id": "yuanshou",
            "lesson_type": "元首",
            "status": "matched" if len(upper_controls) == 1 and not lower_controls else "not_matched",
            "reason": "四课中一处上克下且无下贼上" if len(upper_controls) == 1 and not lower_controls else "未满足唯一上克下条件",
            "source_cards": ["RC-045", "RC-053", "RC-055"],
        },
        {
            "rule_id": "zhongshen",
            "lesson_type": "重审",
            "status": "matched" if len(lower_controls) == 1 and not upper_controls else "not_matched",
            "reason": "四课中一处下贼上且无上克下" if len(lower_controls) == 1 and not upper_controls else "未满足唯一下贼上条件",
            "source_cards": ["RC-048", "RC-051"],
        },
        {
            "rule_id": "biyong",
            "lesson_type": "比用",
            "status": "requires_expert_review" if len(upper_controls) + len(lower_controls) > 1 else "not_matched",
            "reason": "多处克贼候选需按比用法继续择用" if len(upper_controls) + len(lower_controls) > 1 else "未出现多处克贼候选",
            "source_cards": ["RC-059"],
        },
        {
            "rule_id": "shehai",
            "lesson_type": "涉害",
            "status": "requires_expert_review",
            "reason": "MVP 保留规则框架，需专家样例确认涉害深浅算法",
            "source_cards": ["RC-060"],
        },
        {
            "rule_id": "yaoke",
            "lesson_type": "遥克",
            "status": "requires_expert_review" if not upper_controls and not lower_controls and not fuyin and not fanyin else "not_matched",
            "reason": "无直接克贼时可进入遥克候选" if not upper_controls and not lower_controls and not fuyin and not fanyin else "存在其他优先规则或特殊盘式",
            "source_cards": ["RC-061"],
        },
        {
            "rule_id": "maoxing",
            "lesson_type": "昴星",
            "status": "requires_expert_review",
            "reason": "MVP 保留规则框架，需专家确认特定无克条件",
            "source_cards": ["RC-062"],
        },
        {
            "rule_id": "bazhuan",
            "lesson_type": "八专",
            "status": "requires_expert_review",
            "reason": "MVP 保留规则框架，需补充八专日判定表",
            "source_cards": ["RC-063"],
        },
        {
            "rule_id": "bieze",
            "lesson_type": "别责",
            "status": "requires_expert_review",
            "reason": "MVP 保留别责/虽责别名和候选位",
            "source_cards": ["RC-064"],
        },
        {
            "rule_id": "fuyin",
            "lesson_type": "伏吟",
            "status": "matched" if fuyin else "not_matched",
            "reason": "天地盘同位" if fuyin else "天地盘不同位",
            "source_cards": ["RC-065"],
        },
        {
            "rule_id": "fanyin",
            "lesson_type": "返吟",
            "status": "matched" if fanyin else "not_matched",
            "reason": "天地盘相冲同位" if fanyin else "未形成全盘相冲",
            "source_cards": ["RC-065"],
        },
    ]

    if len(upper_controls) == 1 and not lower_controls:
        selected = "yuanshou"
        branches = _follow_sky(upper_controls[0]["upper_branch"], sky)
        transmissions = _transmission_payload(branches, "元首", selected, ["RC-045", "RC-053", "RC-055"], False)
    elif len(lower_controls) == 1 and not upper_controls:
        selected = "zhongshen"
        branches = _follow_sky(lower_controls[0]["upper_branch"], sky)
        transmissions = _transmission_payload(branches, "重审", selected, ["RC-048", "RC-051"], False)
    elif fuyin:
        selected = "fuyin"
        transmissions = _transmission_payload([day_branch, day_branch, day_branch], "伏吟", selected, ["RC-065"], True)
    elif fanyin:
        selected = "fanyin"
        initial = opposite_branch(day_branch)
        transmissions = _transmission_payload(_follow_sky(initial, sky), "返吟", selected, ["RC-065"], True)
    else:
        selected = "pending_expert_review"
        initial = (upper_controls or lower_controls or four_lessons)[0]["upper_branch"]
        transmissions = _transmission_payload(_follow_sky(initial, sky), "待审规则", selected, ["RC-059", "RC-060", "RC-061"], True)

    return transmissions, candidates, selected
