from __future__ import annotations

import json
import inspect
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from xml.sax.saxutils import escape as xml_escape

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import create_liuren_chart, generate_interpretation, retrieve_evidence
from .beta import build_beta_report, load_beta_config, record_beta_feedback
from .canary_run import (
    build_canary_metrics,
    build_canary_task_status,
    build_phase11_report,
    build_public_release_gate,
    load_canary_run_config,
    record_canary_session,
)
from .entertainment import build_share_report, load_general_personas, load_learning_cards
from .growth import (
    build_growth_metrics,
    build_growth_report,
    load_canary_config,
    load_content_calendar,
    load_expert_review_workflow,
    record_growth_event,
    update_expert_review_task,
    validate_canary_access,
)
from .intent import build_non_liuren_response, is_liuren_question
from .knowledge import load_source_cards
from .ops import (
    build_feedback_triage,
    build_ops_metrics,
    build_ops_status,
    record_ops_event,
)
from .openrouter import OpenRouterClient, build_openrouter_messages, openrouter_model
from .realtime import RealtimeSdpClient, build_realtime_session_config
from .release import (
    build_release_metrics,
    build_release_readiness,
    load_legal_document,
    load_release_config,
)
from .public_launch import (
    build_phase12_report,
    build_public_metrics,
    build_public_status,
    load_public_launch_config,
    record_public_incident,
    record_public_session,
)
from .productization import (
    build_phase13_report,
    build_product_metrics,
    build_productization_gate,
    load_learning_path,
    load_productization_config,
    record_learning_progress,
    record_visitor_profile,
)
from .monetization import (
    build_monetization_gate,
    build_monetization_metrics,
    build_phase14_report,
    load_monetization_config,
    load_offer_catalog,
    record_business_lead,
    record_monetization_event,
)
from .payment import (
    build_payment_metrics,
    build_payment_readiness_gate,
    build_phase15_report,
    cancel_sandbox_order,
    confirm_sandbox_payment,
    create_sandbox_checkout,
    load_membership_tiers,
    load_payment_config,
    refund_sandbox_order,
)
from .safety_review import (
    load_copyright_review,
    load_expert_review_cases,
    load_safety_policy,
    validate_beta_readiness,
    validate_safety,
)


ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = ROOT / "static" / "realtime"
RELEASE_STATIC_ROOT = ROOT / "static" / "release"
INDEXABLE_PATHS = (("/", "weekly", "1.0"), ("/app", "weekly", "0.8"))


class LiurenInterpretRequest(BaseModel):
    question: str = Field(min_length=1)
    datetime: str = Field(min_length=1)
    timezone: str = Field(min_length=1)
    location: str | None = None
    category: str | None = None
    mode: Literal["professional", "plain", "story", "mentor"] = "plain"
    tester_id: str | None = None
    invite_code: str | None = None
    manual_params: dict[str, Any] | None = None


class LiurenTextInterpretRequest(LiurenInterpretRequest):
    use_openrouter: bool = True


class ShareReportRequest(BaseModel):
    chart: dict[str, Any]
    interpretation: dict[str, Any]


class SafetyValidateRequest(BaseModel):
    answer: dict[str, Any]
    chart: dict[str, Any]
    mode: Literal["professional", "plain", "story", "mentor"] = "plain"


class OpsReasonRequest(BaseModel):
    reason: str = "manual ops action"


class ExpertReviewUpdateRequest(BaseModel):
    task_id: str | None = None
    rule_id: str | None = None
    expert_opinion: str | None = None
    processing_result: str | None = None
    decision: Literal["approved_for_canary", "blocked_until_reworked", "research_only"] | None = None
    allow_canary: bool | None = None
    status: str | None = None
    reviewer: str | None = None
    notes: str | None = None


class CanarySessionRequest(BaseModel):
    tester_id: str | None = None
    invite_code: str | None = None
    chart_id: str | None = None
    mode: Literal["professional", "plain", "story", "mentor"] = "plain"
    category: str | None = None
    session_status: str = "started"
    feedback_type: str | None = None
    safety_action: str | None = None
    blocked_reasons: list[str] | None = None
    latency_ms: float | None = None
    event_type: str | None = None
    incident_type: str | None = None
    source: str | None = None
    note: str | None = None


class PublicSessionRequest(BaseModel):
    visitor_id: str | None = None
    tester_id: str | None = None
    chart_id: str | None = None
    mode: Literal["professional", "plain", "story", "mentor"] = "plain"
    category: str | None = None
    session_status: str = "started"
    feedback_type: str | None = None
    safety_action: str | None = None
    blocked_reasons: list[str] | None = None
    latency_ms: float | None = None
    event_type: str | None = None
    incident_type: str | None = None
    source: str | None = None
    note: str | None = None
    delete_request: bool | None = None


class PublicIncidentRequest(BaseModel):
    event_type: str = "public_note"
    severity: Literal["P0", "P1", "P2", "P3"] = "P3"
    summary: str | None = None
    chart_id: str | None = None
    visitor_id: str | None = None
    source: str | None = None
    reason: str | None = None


class VisitorProfileRequest(BaseModel):
    visitor_id: str | None = None
    nickname: str | None = None
    mode_preference: Literal["professional", "plain", "story", "mentor"] = "plain"
    source: str | None = None
    note: str | None = None
    delete_request: bool | None = None


class LearningProgressRequest(BaseModel):
    visitor_id: str | None = None
    node_id: str | None = None
    event_type: str = "learning_progress"
    status: str = "started"
    mode: Literal["professional", "plain", "story", "mentor"] = "plain"
    chart_id: str | None = None
    source: str | None = None
    reflection_note: str | None = None
    content_id: str | None = None


class MonetizationEventRequest(BaseModel):
    visitor_id: str | None = None
    event_type: Literal["member_interest", "course_interest", "business_interest", "ip_interest", "pricing_view", "offer_click"] = "offer_click"
    offer_id: str | None = None
    source: str | None = None
    mode: Literal["professional", "plain", "story", "mentor"] | None = None
    note: str | None = None
    delete_request: bool | None = None


class BusinessLeadRequest(BaseModel):
    visitor_id: str | None = None
    contact_nickname: str | None = None
    channel: str | None = None
    need_summary: str | None = None
    source: str | None = None
    offer_id: str | None = None
    delete_request: bool | None = None


class PaymentCheckoutRequest(BaseModel):
    visitor_id: str | None = None
    tier_id: str = "tier-membership-v0"
    currency: str = "CNY"
    amount_cents: int = 0
    source: str | None = None
    note: str | None = None
    delete_request: bool | None = None


class PaymentConfirmRequest(BaseModel):
    order_id: str
    outcome: Literal["success", "failure"] = "success"


class PaymentOrderActionRequest(BaseModel):
    order_id: str
    reason: str | None = None


app = FastAPI(title="RenYu Realtime Prototype", version="0.7.0")
if STATIC_ROOT.exists():
    app.mount("/static/realtime", StaticFiles(directory=STATIC_ROOT), name="realtime-static")
if RELEASE_STATIC_ROOT.exists():
    app.mount("/static/release", StaticFiles(directory=RELEASE_STATIC_ROOT), name="release-static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    if RELEASE_STATIC_ROOT.exists():
        return FileResponse(RELEASE_STATIC_ROOT / "index.html")
    return FileResponse(STATIC_ROOT / "index.html")


@app.get("/app", include_in_schema=False)
def web_app() -> FileResponse:
    return FileResponse(STATIC_ROOT / "index.html")


def _public_base_url(request: Request) -> str:
    configured = os.getenv("PUBLIC_SITE_URL") or os.getenv("VERCEL_PROJECT_PRODUCTION_URL") or os.getenv("VERCEL_URL")
    if configured:
        base = configured.strip().rstrip("/")
        if base and not base.startswith(("http://", "https://")):
            base = f"https://{base}"
        return base
    return str(request.base_url).rstrip("/")


@app.get("/robots.txt", include_in_schema=False)
def robots_txt(request: Request) -> PlainTextResponse:
    base_url = _public_base_url(request)
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /api/",
            f"Sitemap: {base_url}/sitemap.xml",
            "",
        ]
    )
    return PlainTextResponse(content)


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml(request: Request) -> Response:
    base_url = _public_base_url(request)
    lastmod = datetime.now(timezone.utc).date().isoformat()
    url_entries = "\n".join(
        "  <url>\n"
        f"    <loc>{xml_escape(base_url + path)}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>"
        for path, changefreq, priority in INDEXABLE_PATHS
    )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{url_entries}\n"
        "</urlset>\n"
    )
    return Response(content=content, media_type="application/xml")


@app.get("/manifest.webmanifest", include_in_schema=False)
def web_manifest() -> Response:
    content = {
        "name": "澹语 · 大六壬",
        "short_name": "澹语",
        "description": "传统文化学习与娱乐体验，不构成现实建议。",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#f7f3ea",
        "theme_color": "#1e3a8a",
    }
    return Response(json.dumps(content, ensure_ascii=False), media_type="application/manifest+json")


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health")
def health() -> dict[str, Any]:
    try:
        source_card_count = len(load_source_cards(ROOT))
        knowledge_status = "ok"
    except Exception:
        source_card_count = 0
        knowledge_status = "error"
    return {
        "engine": "ok",
        "knowledge": knowledge_status,
        "source_card_count": source_card_count,
        "openai_api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "deepseek_api_key_configured": bool(os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENROUTER_API_KEY")),
        "openrouter_model": openrouter_model(),
        "realtime_model": os.getenv("OPENAI_REALTIME_MODEL", "gpt-realtime"),
        "realtime_voice": os.getenv("OPENAI_REALTIME_VOICE", "marin"),
    }


@app.get("/api/personas")
def personas() -> dict[str, Any]:
    return {"personas": load_general_personas(ROOT)}


@app.get("/api/learning/cards")
def learning_cards() -> dict[str, Any]:
    return {"learning_cards": load_learning_cards(ROOT)}


@app.post("/api/liuren/interpret")
def liuren_interpret(payload: LiurenInterpretRequest) -> dict[str, Any]:
    started = time.perf_counter()
    if not is_liuren_question(payload.question):
        return {
            **build_non_liuren_response(payload.mode),
            "ops_status": build_ops_status(ROOT),
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    ops_status = build_ops_status(ROOT)
    if ops_status["status"] == "paused":
        return {
            "chart": None,
            "evidence": [],
            "interpretation": {
                "mode": payload.mode,
                "overview": "系统已暂停讲盘，仅提供安全说明与反馈入口。",
                "chart_facts": {},
                "evidence": [],
                "rule_reasoning": [],
                "plain_explanation": [],
                "action_prompts": ["请稍后再试，或提交安全/语音体验反馈。"],
                "safety_notice": {"action": "safety_only", "disclaimer": "暂停期间不输出正常讲盘内容。"},
                "ops_status": ops_status,
                "blocked_reasons": ["ops_paused"],
            },
            "safety": {"action": "safety_only", "is_high_risk": True, "risk_type": "ops_paused"},
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    public_status = build_public_status(ROOT)
    if public_status["launch_status"] == "paused":
        return {
            "chart": None,
            "evidence": [],
            "interpretation": {
                "mode": payload.mode,
                "overview": "Public MVP is paused for safety or maintenance review.",
                "chart_facts": {},
                "evidence": [],
                "rule_reasoning": [],
                "plain_explanation": ["Public launch is paused. Only safety and maintenance information is available."],
                "action_prompts": ["Submit feedback or try again after the public pause is lifted."],
                "safety_notice": {"action": "safety_only", "disclaimer": "Paused public launch does not output chart interpretations."},
                "public_status": public_status,
                "blocked_reasons": ["public_paused"],
            },
            "safety": {"action": "safety_only", "is_high_risk": True, "risk_type": "public_paused"},
            "ops_status": ops_status,
            "public_status": public_status,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    if ops_status["status"] == "canary":
        canary_validation = validate_canary_access(
            {"tester_id": payload.tester_id, "invite_code": payload.invite_code},
            root=ROOT,
        )
        if not canary_validation["allowed"]:
            return {
                "chart": None,
                "evidence": [],
                "interpretation": {
                    "mode": payload.mode,
                    "overview": "Canary 准入未通过，仅显示受邀测试说明与安全边界。",
                    "chart_facts": {},
                    "evidence": [],
                    "rule_reasoning": [],
                    "plain_explanation": ["请输入有效测试编号或邀请码后再进入语音起课。"],
                    "action_prompts": ["可先阅读发布说明、安全边界和隐私说明。"],
                    "safety_notice": {"action": "safety_only", "disclaimer": "未通过 canary 准入时不输出正常讲盘内容。"},
                    "ops_status": ops_status,
                    "canary_validation": canary_validation,
                    "blocked_reasons": ["canary_access_denied"],
                },
                "safety": {"action": "safety_only", "is_high_risk": False, "risk_type": "canary_access_denied"},
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
    request = payload.model_dump(exclude_none=True)
    chart = create_liuren_chart(request)
    evidence = retrieve_evidence(chart, query=payload.question, mode=payload.mode)
    interpretation = generate_interpretation(chart, evidence, mode=payload.mode)
    return {
        "chart": chart,
        "evidence": evidence,
        "interpretation": interpretation,
        "safety": chart["safety"],
        "ops_status": ops_status,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
    }


@app.post("/api/liuren/text-interpret")
def liuren_text_interpret(payload: LiurenTextInterpretRequest) -> dict[str, Any]:
    started = time.perf_counter()
    request = payload.model_dump(exclude_none=True)
    base_payload = LiurenInterpretRequest(**payload.model_dump(exclude={"use_openrouter"}))
    response = liuren_interpret(base_payload)
    openrouter = {
        "status": "skipped",
        "model": openrouter_model(),
        "content": "",
        "usage": {},
    }
    if payload.use_openrouter and response.get("chart") is not None:
        try:
            openrouter_client = getattr(app.state, "openrouter_client", None) or OpenRouterClient()
            openrouter = {
                "status": "ok",
                **openrouter_client.create_chat_completion(
                    build_openrouter_messages(request, response["chart"], response["interpretation"]),
                    model=openrouter_model(),
                ),
            }
        except Exception as exc:
            openrouter = {
                "status": "error",
                "model": openrouter_model(),
                "content": "",
                "usage": {},
                "message": str(exc),
            }
    response["openrouter"] = openrouter
    response["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return response


@app.post("/api/report/share")
def report_share(payload: ShareReportRequest) -> dict[str, Any]:
    return build_share_report(payload.chart, payload.interpretation)


@app.get("/api/safety/policy")
def safety_policy() -> dict[str, Any]:
    return load_safety_policy(ROOT)


@app.post("/api/safety/validate")
def safety_validate(payload: SafetyValidateRequest) -> dict[str, Any]:
    return validate_safety(payload.answer, payload.chart, mode=payload.mode)


@app.get("/api/review/status")
def review_status() -> dict[str, Any]:
    expert_review = load_expert_review_cases(ROOT)
    copyright_review = load_copyright_review(ROOT)
    readiness = validate_beta_readiness(
        {
            "expert_cases": expert_review,
            "copyright_review": copyright_review,
            "red_team_passed": True,
            "golden_cases_passed": True,
        }
    )
    return {
        "expert_review": {
            "review_id": expert_review["review_id"],
            "case_count": len(expert_review["cases"]),
            "pending_count": sum(1 for case in expert_review["cases"] if case.get("review_status") in {"pending_expert_review", "needs_expert_review"}),
        },
        "copyright_review": {
            "review_id": copyright_review["review_id"],
            "item_count": len(copyright_review["items"]),
            "blocked_count": sum(1 for item in copyright_review["items"] if item.get("beta_status") == "blocked"),
        },
        "beta_readiness": readiness,
    }


@app.get("/api/beta/config")
def beta_config() -> dict[str, Any]:
    return load_beta_config(ROOT)


@app.post("/api/beta/feedback")
def beta_feedback(payload: dict[str, Any]) -> dict[str, Any]:
    record = record_beta_feedback(payload, ROOT)
    return {"stored": True, "feedback": record}


@app.get("/api/beta/report")
def beta_report() -> dict[str, Any]:
    return build_beta_report(ROOT)


@app.get("/api/release/config")
def release_config() -> dict[str, Any]:
    return load_release_config(ROOT)


@app.get("/api/release/readiness")
def release_readiness() -> dict[str, Any]:
    return build_release_readiness(ROOT)


@app.get("/api/release/metrics")
def release_metrics() -> dict[str, Any]:
    return build_release_metrics(ROOT)


@app.get("/api/legal/privacy")
def legal_privacy() -> dict[str, Any]:
    return load_legal_document("privacy", ROOT)


@app.get("/api/legal/safety")
def legal_safety() -> dict[str, Any]:
    return load_legal_document("safety", ROOT)


@app.get("/api/legal/copyright")
def legal_copyright() -> dict[str, Any]:
    return load_legal_document("copyright", ROOT)


@app.get("/api/ops/status")
def ops_status() -> dict[str, Any]:
    return build_ops_status(ROOT)


@app.get("/api/ops/metrics")
def ops_metrics() -> dict[str, Any]:
    return build_ops_metrics(ROOT)


@app.get("/api/ops/feedback/triage")
def ops_feedback_triage() -> dict[str, Any]:
    return build_feedback_triage(ROOT)


@app.post("/api/ops/event")
def ops_event(payload: dict[str, Any]) -> dict[str, Any]:
    event = record_ops_event(payload, ROOT)
    return {"stored": True, "event": event, "status": build_ops_status(ROOT)}


@app.post("/api/ops/pause")
def ops_pause(payload: OpsReasonRequest) -> dict[str, Any]:
    event = record_ops_event({"event_type": "manual_pause", "severity": "P1", "summary": payload.reason, "reason": payload.reason}, ROOT)
    return {"stored": True, "event": event, "status": build_ops_status(ROOT)}


@app.post("/api/ops/resume")
def ops_resume(payload: OpsReasonRequest) -> dict[str, Any]:
    event = record_ops_event({"event_type": "manual_resume", "severity": "P3", "summary": payload.reason, "reason": payload.reason}, ROOT)
    return {"stored": True, "event": event, "status": build_ops_status(ROOT)}


@app.get("/api/expert/review/tasks")
def expert_review_tasks() -> dict[str, Any]:
    return load_expert_review_workflow(ROOT)


@app.post("/api/expert/review/update")
def expert_review_update(payload: ExpertReviewUpdateRequest) -> dict[str, Any]:
    try:
        return update_expert_review_task(payload.model_dump(exclude_none=True), ROOT)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/canary/config")
def canary_config() -> dict[str, Any]:
    return load_canary_config(ROOT)


@app.post("/api/canary/validate")
def canary_validate(payload: dict[str, Any]) -> dict[str, Any]:
    return validate_canary_access(payload, root=ROOT)


@app.get("/api/content/calendar")
def content_calendar() -> dict[str, Any]:
    return load_content_calendar(ROOT)


@app.get("/api/growth/metrics")
def growth_metrics() -> dict[str, Any]:
    return build_growth_metrics(ROOT)


@app.post("/api/growth/event")
def growth_event(payload: dict[str, Any]) -> dict[str, Any]:
    event = record_growth_event(payload, ROOT)
    return {"stored": True, "event": event, "metrics": build_growth_metrics(ROOT)}


@app.get("/api/growth/report")
def growth_report() -> dict[str, Any]:
    return build_growth_report(ROOT)


@app.get("/api/canary/run/config")
def canary_run_config() -> dict[str, Any]:
    return load_canary_run_config(ROOT)


@app.get("/api/canary/tasks/status")
def canary_tasks_status(tester_id: str | None = None, invite_code: str | None = None) -> dict[str, Any]:
    return build_canary_task_status(ROOT, tester_id=tester_id, invite_code=invite_code)


@app.post("/api/canary/session")
def canary_session(payload: CanarySessionRequest) -> dict[str, Any]:
    ops_state = build_ops_status(ROOT)
    if ops_state.get("status") != "canary":
        return {
            "stored": False,
            "blocked_reasons": ["canary_not_active"],
            "ops_status": ops_state,
        }
    validation = validate_canary_access({"tester_id": payload.tester_id, "invite_code": payload.invite_code}, root=ROOT)
    if not validation["allowed"]:
        return {
            "stored": False,
            "blocked_reasons": ["canary_access_denied"],
            "canary_validation": validation,
            "ops_status": ops_state,
        }
    record = record_canary_session(payload.model_dump(exclude_none=True), ROOT)
    return {"stored": True, "session": record, "metrics": build_canary_metrics(ROOT)}


@app.get("/api/canary/metrics")
def canary_metrics() -> dict[str, Any]:
    return build_canary_metrics(ROOT)


@app.get("/api/public-release/gate")
def public_release_gate() -> dict[str, Any]:
    return build_public_release_gate(ROOT)


@app.get("/api/phase11/report")
def phase11_report() -> dict[str, Any]:
    return build_phase11_report(ROOT)


@app.get("/api/public/config")
def public_config() -> dict[str, Any]:
    return load_public_launch_config(ROOT)


@app.get("/api/public/status")
def public_status() -> dict[str, Any]:
    return build_public_status(ROOT)


@app.post("/api/public/session")
def public_session(payload: PublicSessionRequest) -> dict[str, Any]:
    status = build_public_status(ROOT)
    if status.get("launch_status") not in {"preview", "live"}:
        return {
            "stored": False,
            "blocked_reasons": ["public_not_active"],
            "status": status,
        }
    record = record_public_session(payload.model_dump(exclude_none=True), ROOT)
    return {"stored": True, "session": record, "metrics": build_public_metrics(ROOT), "status": status}


@app.get("/api/public/metrics")
def public_metrics() -> dict[str, Any]:
    return build_public_metrics(ROOT)


@app.post("/api/public/incident")
def public_incident(payload: PublicIncidentRequest) -> dict[str, Any]:
    record = record_public_incident(payload.model_dump(exclude_none=True), ROOT)
    return {"stored": True, "incident": record, "status": build_public_status(ROOT)}


@app.post("/api/public/pause")
def public_pause(payload: OpsReasonRequest) -> dict[str, Any]:
    record = record_public_incident(
        {
            "event_type": "manual_public_pause",
            "severity": "P1",
            "summary": payload.reason,
            "reason": payload.reason,
        },
        ROOT,
    )
    return {"stored": True, "incident": record, "status": build_public_status(ROOT)}


@app.post("/api/public/resume")
def public_resume(payload: OpsReasonRequest) -> dict[str, Any]:
    record = record_public_incident(
        {
            "event_type": "manual_public_resume",
            "severity": "P3",
            "summary": payload.reason,
            "reason": payload.reason,
        },
        ROOT,
    )
    return {"stored": True, "incident": record, "status": build_public_status(ROOT)}


@app.get("/api/phase12/report")
def phase12_report() -> dict[str, Any]:
    return build_phase12_report(ROOT)


@app.get("/api/productization/config")
def productization_config() -> dict[str, Any]:
    return load_productization_config(ROOT)


@app.get("/api/productization/gate")
def productization_gate() -> dict[str, Any]:
    return build_productization_gate(ROOT)


@app.post("/api/visitor/profile")
def visitor_profile(payload: VisitorProfileRequest) -> dict[str, Any]:
    gate = build_productization_gate(ROOT)
    if gate.get("gate_status") != "experiment":
        return {
            "stored": False,
            "blocked_reasons": ["productization_not_active"],
            "gate": gate,
        }
    profile = record_visitor_profile(payload.model_dump(exclude_none=True), ROOT)
    return {"stored": True, "profile": profile, "gate": gate, "metrics": build_product_metrics(ROOT)}


@app.get("/api/learning/path")
def learning_path() -> dict[str, Any]:
    return load_learning_path(ROOT)


@app.post("/api/learning/progress")
def learning_progress(payload: LearningProgressRequest) -> dict[str, Any]:
    gate = build_productization_gate(ROOT)
    if gate.get("gate_status") != "experiment":
        return {
            "stored": False,
            "blocked_reasons": ["productization_not_active"],
            "gate": gate,
        }
    progress = record_learning_progress(payload.model_dump(exclude_none=True), ROOT)
    return {"stored": True, "progress": progress, "gate": gate, "metrics": build_product_metrics(ROOT)}


@app.get("/api/product/metrics")
def product_metrics() -> dict[str, Any]:
    return build_product_metrics(ROOT)


@app.get("/api/phase13/report")
def phase13_report() -> dict[str, Any]:
    return build_phase13_report(ROOT)


@app.get("/api/monetization/config")
def monetization_config() -> dict[str, Any]:
    return load_monetization_config(ROOT)


@app.get("/api/monetization/gate")
def monetization_gate() -> dict[str, Any]:
    return build_monetization_gate(ROOT)


@app.get("/api/monetization/offers")
def monetization_offers() -> dict[str, Any]:
    return load_offer_catalog(ROOT)


@app.post("/api/monetization/event")
def monetization_event(payload: MonetizationEventRequest) -> dict[str, Any]:
    gate = build_monetization_gate(ROOT)
    if gate.get("gate_status") != "experiment":
        return {
            "stored": False,
            "blocked_reasons": ["monetization_not_active"],
            "gate": gate,
        }
    event = record_monetization_event(payload.model_dump(exclude_none=True), ROOT)
    return {"stored": True, "event": event, "gate": gate, "metrics": build_monetization_metrics(ROOT)}


@app.post("/api/business/lead")
def business_lead(payload: BusinessLeadRequest) -> dict[str, Any]:
    gate = build_monetization_gate(ROOT)
    if gate.get("gate_status") != "experiment":
        return {
            "stored": False,
            "blocked_reasons": ["monetization_not_active"],
            "gate": gate,
        }
    lead = record_business_lead(payload.model_dump(exclude_none=True), ROOT)
    return {"stored": True, "lead": lead, "gate": gate, "metrics": build_monetization_metrics(ROOT)}


@app.get("/api/monetization/metrics")
def monetization_metrics() -> dict[str, Any]:
    return build_monetization_metrics(ROOT)


@app.get("/api/phase14/report")
def phase14_report() -> dict[str, Any]:
    return build_phase14_report(ROOT)


@app.get("/api/payment/config")
def payment_config() -> dict[str, Any]:
    return load_payment_config(ROOT)


@app.get("/api/payment/gate")
def payment_gate() -> dict[str, Any]:
    return build_payment_readiness_gate(ROOT)


@app.get("/api/membership/tiers")
def membership_tiers() -> dict[str, Any]:
    return load_membership_tiers(ROOT)


@app.post("/api/payment/checkout")
def payment_checkout(payload: PaymentCheckoutRequest) -> dict[str, Any]:
    gate = build_payment_readiness_gate(ROOT)
    if gate.get("gate_status") != "sandbox":
        return {
            "stored": False,
            "blocked_reasons": ["payment_not_active"],
            "gate": gate,
        }
    result = create_sandbox_checkout(payload.model_dump(exclude_none=True), ROOT)
    return {"stored": True, **result, "gate": gate, "metrics": build_payment_metrics(ROOT)}


@app.post("/api/payment/sandbox/confirm")
def payment_sandbox_confirm(payload: PaymentConfirmRequest) -> dict[str, Any]:
    gate = build_payment_readiness_gate(ROOT)
    if gate.get("gate_status") != "sandbox":
        return {
            "stored": False,
            "blocked_reasons": ["payment_not_active"],
            "gate": gate,
        }
    result = confirm_sandbox_payment(payload.order_id, outcome=payload.outcome, root=ROOT)
    return {"stored": True, **result, "gate": gate, "metrics": build_payment_metrics(ROOT)}


@app.post("/api/payment/cancel")
def payment_cancel(payload: PaymentOrderActionRequest) -> dict[str, Any]:
    gate = build_payment_readiness_gate(ROOT)
    if gate.get("gate_status") != "sandbox":
        return {
            "stored": False,
            "blocked_reasons": ["payment_not_active"],
            "gate": gate,
        }
    result = cancel_sandbox_order(payload.order_id, reason=payload.reason or "", root=ROOT)
    return {"stored": True, **result, "gate": gate, "metrics": build_payment_metrics(ROOT)}


@app.post("/api/payment/refund")
def payment_refund(payload: PaymentOrderActionRequest) -> dict[str, Any]:
    gate = build_payment_readiness_gate(ROOT)
    if gate.get("gate_status") != "sandbox":
        return {
            "stored": False,
            "blocked_reasons": ["payment_not_active"],
            "gate": gate,
        }
    result = refund_sandbox_order(payload.order_id, reason=payload.reason or "", root=ROOT)
    return {"stored": True, **result, "gate": gate, "metrics": build_payment_metrics(ROOT)}


@app.get("/api/payment/metrics")
def payment_metrics() -> dict[str, Any]:
    return build_payment_metrics(ROOT)


@app.get("/api/phase15/report")
def phase15_report() -> dict[str, Any]:
    return build_phase15_report(ROOT)


@app.post("/api/realtime/session", response_class=PlainTextResponse)
async def realtime_session(request: Request) -> PlainTextResponse:
    sdp_offer = (await request.body()).decode("utf-8", errors="replace")
    if not sdp_offer.strip():
        raise HTTPException(status_code=400, detail="SDP offer is required")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured on the server")

    session_config = build_realtime_session_config()
    realtime_client = getattr(app.state, "realtime_client", None) or RealtimeSdpClient()
    result = realtime_client.create_call(sdp_offer, session_config)
    if inspect.isawaitable(result):
        result = await result
    return PlainTextResponse(str(result), media_type="application/sdp")


def main() -> int:
    uvicorn.run("liuren_engine.webapp:app", host="127.0.0.1", port=8000, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
