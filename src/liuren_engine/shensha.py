from __future__ import annotations

from .relations import void_branches


def build_basic_shensha(day_ganzhi: str, four_lessons: list[dict]) -> list[dict]:
    shensha: list[dict] = []
    for branch in void_branches(day_ganzhi):
        shensha.append(
            {
                "name": "空亡",
                "branch": branch,
                "effect": "auxiliary_reference_only",
                "source_cards": ["RC-030", "RV-010"],
            }
        )

    seen: set[tuple[str, str]] = set()
    for lesson in four_lessons:
        for interaction in lesson["interactions_with_day_branch"]:
            key = (interaction, lesson["upper_branch"])
            if interaction == "same_branch" or key in seen:
                continue
            seen.add(key)
            shensha.append(
                {
                    "name": interaction,
                    "branch": lesson["upper_branch"],
                    "effect": "auxiliary_reference_only",
                    "source_cards": ["G-050", "RC-009"],
                }
            )
    return shensha
