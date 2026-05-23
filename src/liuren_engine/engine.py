from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .calendar import build_ganzhi_payload, divination_hour, month_general, normalize_datetime
from .constants import SCHOOL_VERSION
from .generals import build_generals
from .lessons import build_four_lessons
from .plates import build_earth_plate, build_heaven_plate, sky_map
from .safety import build_safety, category_symbols, normalize_category
from .shensha import build_basic_shensha
from .transmissions import build_three_transmissions


def _manual_params(request: Mapping[str, Any]) -> dict:
    params = dict(request.get("manual_params") or {})
    params.setdefault("school_version", SCHOOL_VERSION)
    return params


def _chart_id(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return "chart_" + hashlib.sha256(encoded).hexdigest()[:16]


def create_liuren_chart(request: Mapping[str, Any]) -> dict:
    """Create a deterministic Da Liu Ren chart JSON payload.

    This MVP intentionally records unverified formulas in rule_trace instead of
    presenting them as final school doctrine.
    """

    params = _manual_params(request)
    school_version = params.get("school_version", SCHOOL_VERSION)
    if school_version != SCHOOL_VERSION:
        raise ValueError(f"unsupported school_version: {school_version}")

    dt = normalize_datetime(str(request.get("datetime", "")), str(request.get("timezone", "")))
    raw_category = request.get("category")
    question = str(request.get("question") or "")
    category = normalize_category(raw_category if isinstance(raw_category, str) else None, question)
    ganzhi, ganzhi_trace = build_ganzhi_payload(dt, params)
    month_general_value, month_policy = month_general(dt, params)
    hour_branch, hour_policy = divination_hour(dt, params)

    earth_plate = build_earth_plate()
    heaven_plate = build_heaven_plate(month_general_value, hour_branch)
    sky = sky_map(heaven_plate)
    four_lessons = build_four_lessons(ganzhi["day"], sky)
    transmissions, candidates, selected_rule = build_three_transmissions(
        four_lessons=four_lessons,
        sky=sky,
        heaven_plate=heaven_plate,
        day_branch=ganzhi["day_branch"],
    )
    generals, general_trace = build_generals(ganzhi["day_stem"], dt.hour, params)
    shensha = build_basic_shensha(ganzhi["day"], four_lessons)
    safety = build_safety(category if isinstance(category, str) else None)

    identity_payload = {
        "question": request.get("question"),
        "datetime": dt.isoformat(),
        "timezone": request.get("timezone"),
        "category": category,
        "raw_category": raw_category if raw_category != category else None,
        "manual_params": params,
    }

    rule_trace = {
        "school_version": school_version,
        "month_general_policy": month_policy,
        "divination_hour_policy": hour_policy,
        "divination_hour": hour_branch,
        "general_policy": "nobleman_day_night_and_direction_v0_needs_expert_review",
        "transmission_candidates": candidates,
        "selected_transmission_rule": selected_rule,
        "category_symbols": category_symbols(category if isinstance(category, str) else None),
        **ganzhi_trace,
        **general_trace,
    }
    if raw_category != category:
        rule_trace["raw_category"] = raw_category

    return {
        "chart_id": _chart_id(identity_payload),
        "school_version": school_version,
        "question": request.get("question"),
        "category": category,
        "datetime_normalized": dt.isoformat(),
        "timezone": request.get("timezone"),
        "location": request.get("location"),
        "ganzhi": ganzhi,
        "month_general": month_general_value,
        "earth_plate": earth_plate,
        "heaven_plate": heaven_plate,
        "four_lessons": four_lessons,
        "three_transmissions": transmissions,
        "generals": generals,
        "shensha": shensha,
        "safety": safety,
        "rule_trace": rule_trace,
    }
