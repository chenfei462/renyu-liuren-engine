from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from .constants import BRANCHES, SCHOOL_VERSION, STEMS


ANCHOR_DATE = date(2024, 2, 10)
ANCHOR_DAY_INDEX = 40  # 甲辰, 0-based sexagenary index.


def normalize_datetime(value: str, timezone_name: str) -> datetime:
    if not value:
        raise ValueError("datetime is required")
    if not timezone_name:
        raise ValueError("timezone is required")

    tz = ZoneInfo(timezone_name)
    normalized_value = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized_value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def branch_for_hour(dt: datetime) -> str:
    hour = dt.hour
    if hour == 23 or hour == 0:
        return "子"
    return BRANCHES[((hour + 1) // 2) % 12]


def sexagenary_index_for_day(day: date) -> int:
    return (ANCHOR_DAY_INDEX + (day - ANCHOR_DATE).days) % 60


def ganzhi_from_index(index: int) -> str:
    return STEMS[index % 10] + BRANCHES[index % 12]


def day_ganzhi(dt: datetime, manual_params: dict) -> tuple[str, str]:
    manual = manual_params.get("ganzhi_day")
    if manual:
        if len(manual) < 2 or manual[0] not in STEMS or manual[1:] not in BRANCHES:
            raise ValueError("manual_params.ganzhi_day must be a valid stem-branch value")
        return manual, "manual_override"
    return ganzhi_from_index(sexagenary_index_for_day(dt.date())), "anchored_gregorian_day_v0"


def year_ganzhi(dt: datetime) -> str:
    index = (dt.year - 1984) % 60
    return ganzhi_from_index(index)


def month_general(dt: datetime, manual_params: dict) -> tuple[str, str]:
    manual = manual_params.get("month_general")
    if manual:
        if manual not in BRANCHES:
            raise ValueError("manual_params.month_general must be one of the twelve branches")
        return manual, "manual_override"

    month_to_general = {
        1: "子",
        2: "亥",
        3: "戌",
        4: "酉",
        5: "申",
        6: "未",
        7: "午",
        8: "巳",
        9: "辰",
        10: "卯",
        11: "寅",
        12: "丑",
    }
    return month_to_general[dt.month], "approximate_gregorian_month_v0_needs_expert_review"


def divination_hour(dt: datetime, manual_params: dict) -> tuple[str, str]:
    manual = manual_params.get("divination_hour")
    if manual:
        if manual not in BRANCHES:
            raise ValueError("manual_params.divination_hour must be one of the twelve branches")
        return manual, "manual_override"
    return branch_for_hour(dt), "local_two_hour_branch_v0"


def build_ganzhi_payload(dt: datetime, manual_params: dict) -> tuple[dict, dict]:
    day, day_policy = day_ganzhi(dt, manual_params)
    return (
        {
            "year": year_ganzhi(dt),
            "day": day,
            "day_stem": day[0],
            "day_branch": day[1:],
        },
        {
            "day_ganzhi_policy": day_policy,
            "school_version": manual_params.get("school_version", SCHOOL_VERSION),
        },
    )
