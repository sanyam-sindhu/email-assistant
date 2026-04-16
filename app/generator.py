from __future__ import annotations

import os
from typing import Literal

import anthropic
from openai import OpenAI

from .prompts import build_full_prompt

Provider = Literal["claude", "openai"]


def _claude_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def _openai_client() -> OpenAI:
    return OpenAI()


def generate_email(
    intent: str,
    key_facts: list[str],
    tone: str,
    provider: Provider = "claude",
    model: str | None = None,
) -> str:
    system, user = build_full_prompt(intent, key_facts, tone)

    if provider == "claude":
        model = model or os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")
        client = _claude_client()
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return next(b.text for b in response.content if b.type == "text").strip()

    if provider == "openai":
        model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        client = _openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()

    raise ValueError(f"unknown provider: {provider}")
