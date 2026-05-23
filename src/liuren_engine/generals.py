from __future__ import annotations

from .constants import BRANCHES, GENERAL_NAMES, NOBLEMAN_START


def _day_or_night(hour: int, manual_params: dict) -> tuple[str, str]:
    manual = manual_params.get("nobleman_day_night")
    if manual:
        if manual not in {"day", "night"}:
            raise ValueError("manual_params.nobleman_day_night must be day or night")
        return manual, "manual_override"
    return ("day", "local_hour_6_to_17_day_v0") if 6 <= hour <= 17 else ("night", "local_hour_18_to_5_night_v0")


def build_generals(day_stem: str, hour: int, manual_params: dict) -> tuple[list[dict], dict]:
    day_part, day_part_policy = _day_or_night(hour, manual_params)
    start_branch = manual_params.get("nobleman_start") or NOBLEMAN_START[day_stem][day_part]
    if start_branch not in BRANCHES:
        raise ValueError("manual_params.nobleman_start must be one of the twelve branches")

    manual_direction = manual_params.get("general_direction")
    if manual_direction:
        if manual_direction not in {"forward", "reverse"}:
            raise ValueError("manual_params.general_direction must be forward or reverse")
        direction = manual_direction
        direction_policy = "manual_override"
    else:
        direction = "forward" if BRANCHES.index(start_branch) <= BRANCHES.index("辰") else "reverse"
        direction_policy = "start_branch_half_plate_v0_needs_expert_review"

    start_index = BRANCHES.index(start_branch)
    generals: list[dict] = []
    for offset, name in enumerate(GENERAL_NAMES):
        branch_index = (start_index + offset) % 12 if direction == "forward" else (start_index - offset) % 12
        generals.append(
            {
                "sequence": offset + 1,
                "general": name,
                "earth_branch": BRANCHES[branch_index],
                "day_part": day_part,
            }
        )

    trace = {
        "nobleman_day_night_policy": day_part_policy,
        "nobleman_start": start_branch,
        "general_direction": direction,
        "general_direction_policy": direction_policy,
    }
    return generals, trace
