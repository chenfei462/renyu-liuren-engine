from __future__ import annotations

from .constants import STEM_HOME_BRANCH
from .relations import branch_interactions, element_relation, void_branches


def build_four_lessons(day_ganzhi: str, sky: dict[str, str]) -> list[dict]:
    day_stem = day_ganzhi[0]
    day_branch = day_ganzhi[1:]
    stem_home = STEM_HOME_BRANCH[day_stem]
    voids = set(void_branches(day_ganzhi))

    first_lower = stem_home
    first_upper = sky[first_lower]
    second_lower = first_upper
    second_upper = sky[second_lower]
    third_lower = day_branch
    third_upper = sky[third_lower]
    fourth_lower = third_upper
    fourth_upper = sky[fourth_lower]

    raw = [
        ("日干寄宫", first_lower, first_upper),
        ("第一课上神", second_lower, second_upper),
        ("日支", third_lower, third_upper),
        ("第三课上神", fourth_lower, fourth_upper),
    ]

    lessons: list[dict] = []
    for index, (role, lower, upper) in enumerate(raw, start=1):
        lessons.append(
            {
                "lesson": index,
                "lower_role": role,
                "lower_branch": lower,
                "upper_branch": upper,
                "relation": element_relation(upper, lower),
                "interactions_with_day_branch": branch_interactions(upper, day_branch),
                "upper_is_void": upper in voids,
                "lower_is_void": lower in voids,
                "source_rule": "stem_home_and_day_branch_four_lessons_v0_needs_expert_review",
            }
        )
    return lessons
