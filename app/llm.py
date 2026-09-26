from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


class LLMError(RuntimeError):
    pass


def client() -> OpenAI:
    if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-your-key"):
        raise LLMError("未配置 OPENAI_API_KEY。请复制 .env.example 为 .env 并填入密钥。")
    return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


def complete(system: str, user: str, *, json_mode: bool = False, temperature: float = 0.4) -> str:
    kwargs: dict[str, Any] = {
        "model": OPENAI_MODEL,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        resp = client().chat.completions.create(**kwargs)
    except Exception as e:  # noqa: BLE001
        raise LLMError(str(e)) from e
    text = (resp.choices[0].message.content or "").strip()
    if not text:
        raise LLMError("模型返回空内容")
    return text


def complete_json(system: str, user: str, temperature: float = 0.2) -> dict[str, Any]:
    raw = complete(system, user, json_mode=True, temperature=temperature)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise LLMError(f"模型未返回合法 JSON: {raw[:400]}") from e
    if not isinstance(data, dict):
        raise LLMError("JSON 根节点必须是对象")
    return data
