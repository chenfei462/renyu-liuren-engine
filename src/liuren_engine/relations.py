from __future__ import annotations

from .constants import BRANCH_ELEMENTS, BRANCHES, CONTROLS, GENERATES, STEMS


def branch_index(branch: str) -> int:
    return BRANCHES.index(branch)


def element_relation(upper_branch: str, lower_branch: str) -> str:
    upper = BRANCH_ELEMENTS[upper_branch]
    lower = BRANCH_ELEMENTS[lower_branch]
    if upper == lower:
        return "same_element"
    if CONTROLS[upper] == lower:
        return "upper_controls_lower"
    if CONTROLS[lower] == upper:
        return "lower_controls_upper"
    if GENERATES[upper] == lower:
        return "upper_generates_lower"
    if GENERATES[lower] == upper:
        return "lower_generates_upper"
    return "neutral"


def opposite_branch(branch: str) -> str:
    return BRANCHES[(branch_index(branch) + 6) % 12]


def clashes(branch_a: str, branch_b: str) -> bool:
    return opposite_branch(branch_a) == branch_b


COMBINE_PAIRS = {frozenset(pair) for pair in [("子", "丑"), ("寅", "亥"), ("卯", "戌"), ("辰", "酉"), ("巳", "申"), ("午", "未")]}
HARM_PAIRS = {frozenset(pair) for pair in [("子", "未"), ("丑", "午"), ("寅", "巳"), ("卯", "辰"), ("申", "亥"), ("酉", "戌")]}
PUNISHMENT_PAIRS = {frozenset(pair) for pair in [("子", "卯"), ("寅", "巳"), ("巳", "申"), ("丑", "戌"), ("戌", "未")]}


def branch_interactions(branch_a: str, branch_b: str) -> list[str]:
    interactions: list[str] = []
    pair = frozenset((branch_a, branch_b))
    if branch_a == branch_b:
        interactions.append("same_branch")
    if clashes(branch_a, branch_b):
        interactions.append("chong")
    if pair in COMBINE_PAIRS:
        interactions.append("he")
    if pair in HARM_PAIRS:
        interactions.append("hai")
    if pair in PUNISHMENT_PAIRS:
        interactions.append("xing")
    return interactions


def sexagenary_index(ganzhi: str) -> int:
    stem = ganzhi[0]
    branch = ganzhi[1:]
    for index in range(60):
        if STEMS[index % 10] == stem and BRANCHES[index % 12] == branch:
            return index
    raise ValueError(f"invalid sexagenary value: {ganzhi}")


def void_branches(day_ganzhi: str) -> list[str]:
    index = sexagenary_index(day_ganzhi)
    start = index - (index % 10)
    used = {BRANCHES[(start + offset) % 12] for offset in range(10)}
    return [branch for branch in BRANCHES if branch not in used]
