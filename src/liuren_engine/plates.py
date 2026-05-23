from __future__ import annotations

from .constants import BRANCH_ELEMENTS, BRANCHES


def build_earth_plate() -> list[dict]:
    return [
        {
            "index": index,
            "earth_branch": branch,
            "element": BRANCH_ELEMENTS[branch],
        }
        for index, branch in enumerate(BRANCHES)
    ]


def build_heaven_plate(month_general: str, divination_hour: str) -> list[dict]:
    month_index = BRANCHES.index(month_general)
    hour_index = BRANCHES.index(divination_hour)
    plate: list[dict] = []
    for earth_index, earth_branch in enumerate(BRANCHES):
        heaven_branch = BRANCHES[(month_index + earth_index - hour_index) % 12]
        plate.append(
            {
                "earth_branch": earth_branch,
                "heaven_branch": heaven_branch,
                "rule": "month_general_added_to_divination_hour",
            }
        )
    return plate


def sky_map(heaven_plate: list[dict]) -> dict[str, str]:
    return {item["earth_branch"]: item["heaven_branch"] for item in heaven_plate}
