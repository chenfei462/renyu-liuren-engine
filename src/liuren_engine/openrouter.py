from __future__ import annotations

import os
from typing import Any, Sequence

import httpx


DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"


def deepseek_chat_completions_url() -> str:
    base_url = os.getenv("DEEPSEEK_BASE_URL") or os.getenv("OPENROUTER_BASE_URL") or DEFAULT_DEEPSEEK_BASE_URL
    return base_url.rstrip("/") + "/chat/completions"


def openrouter_model() -> str:
    return os.getenv("DEEPSEEK_MODEL") or os.getenv("OPENROUTER_MODEL") or DEFAULT_DEEPSEEK_MODEL


class OpenRouterClient:
    def __init__(self, api_key: str | None = None, timeout: float = 30):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENROUTER_API_KEY", "")
        self.timeout = timeout

    def create_chat_completion(self, messages: Sequence[dict[str, str]], model: str | None = None) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is required on the server")
        selected_model = model or openrouter_model()
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                deepseek_chat_completions_url(),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": selected_model,
                    "messages": list(messages),
                },
            )
            response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices") or []
        message = choices[0].get("message", {}) if choices else {}
        return {
            "model": payload.get("model") or selected_model,
            "content": message.get("content") or "",
            "usage": payload.get("usage") or {},
        }


def build_openrouter_messages(
    request: dict[str, Any],
    chart: dict[str, Any],
    interpretation: dict[str, Any],
) -> list[dict[str, str]]:
    compact_payload = {
        "question": request.get("question"),
        "mode": request.get("mode"),
        "category": chart.get("category"),
        "safety": chart.get("safety"),
        "question_focus": interpretation.get("question_focus", {}),
        "overview": interpretation.get("overview"),
        "plain_explanation": interpretation.get("plain_explanation", []),
        "action_prompts": interpretation.get("action_prompts", []),
        "blocked_reasons": interpretation.get("blocked_reasons", []),
    }
    return [
        {
            "role": "system",
            "content": (
                "你是壬语的中文解释润色助手。只基于用户提供的本地排盘 JSON 改写，"
                "不得新增排盘事实、不得承诺现实结果。输出简洁中文，保留传统文化学习与娱乐边界。"
                "第一句必须围绕用户原问题作答，说明这件事从观察框架看要注意什么。"
                "不要只输出通用产品说明。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请把下面本地六壬解释整理成更自然的中文摘要，分为「概览」「可观察线索」「下一步」。"
                "必须反复贴合 question，不要脱离原问题写通用模板。\n"
                f"{compact_payload}"
            ),
        },
    ]
