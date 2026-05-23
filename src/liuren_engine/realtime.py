from __future__ import annotations

import json
import os
from typing import Any

import httpx


REALTIME_CALLS_URL = "https://api.openai.com/v1/realtime/calls"


def realtime_model() -> str:
    return os.getenv("OPENAI_REALTIME_MODEL", "gpt-realtime")


def realtime_voice() -> str:
    return os.getenv("OPENAI_REALTIME_VOICE", "marin")


def build_realtime_session_config() -> dict[str, Any]:
    return {
        "type": "realtime",
        "model": realtime_model(),
        "output_modalities": ["audio", "text"],
        "instructions": (
            "当前是受限 Beta：只提供传统文化学习与娱乐体验，不构成现实建议。"
            "你是壬语实时语音代理。不得自行排盘，不得伪造出处。"
            "需要起课、检索或解释时，必须调用 create_liuren_interpretation 工具，"
            "并且只基于工具返回的 chart、evidence、interpretation 回答。"
            "故事版是娱乐表达，导师版是学习解释，只能改变讲述方式，不能补造规则或现实结论。"
            "回答前必须检查工具返回的 interpretation.safety_validation 与 blocked_reasons；"
            "若 blocked_reasons 非空，只播报安全降级或拒绝伪造依据的内容。"
            "遇到医疗、法律、投资、人身安全等高风险内容，只播报安全降级提示和反思清单。"
        ),
        "audio": {
            "input": {
                "turn_detection": {"type": "semantic_vad"},
            },
            "output": {
                "voice": realtime_voice(),
            },
        },
        "tools": [
            {
                "type": "function",
                "name": "create_liuren_interpretation",
                "description": "Create a Da Liu Ren chart and evidence-backed interpretation using the local RenYu engine.",
                "parameters": {
                    "type": "object",
                    "required": ["question", "datetime", "timezone"],
                    "properties": {
                        "question": {"type": "string", "description": "The user's question."},
                        "datetime": {"type": "string", "description": "ISO-8601 divination datetime."},
                        "timezone": {"type": "string", "description": "IANA timezone, e.g. Asia/Shanghai."},
                        "location": {"type": ["string", "null"]},
                        "category": {"type": ["string", "null"]},
                        "mode": {"type": "string", "enum": ["professional", "plain", "story", "mentor"]},
                        "tester_id": {"type": ["string", "null"], "description": "Canary tester id when available."},
                        "invite_code": {"type": ["string", "null"], "description": "Canary invite code when available."},
                    },
                    "additionalProperties": False,
                },
            }
        ],
        "tool_choice": "auto",
    }


class RealtimeSdpClient:
    def __init__(self, api_key: str | None = None, timeout: float = 30):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.timeout = timeout

    def create_call(self, sdp_offer: str, session_config: dict[str, Any]) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required on the server")
        files = {
            "sdp": ("offer.sdp", sdp_offer, "application/sdp"),
            "session": ("session.json", json.dumps(session_config, ensure_ascii=False), "application/json"),
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                REALTIME_CALLS_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files,
            )
            response.raise_for_status()
            return response.text
