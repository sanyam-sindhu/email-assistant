from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .generator import generate_email

load_dotenv()

app = FastAPI(
    title="Email Generation Assistant",
    description="Role-Playing + Few-Shot prompted email drafter. Claude vs GPT.",
    version="1.0.0",
)


class GenerateRequest(BaseModel):
    intent: str = Field(..., min_length=3)
    key_facts: list[str] = Field(..., min_length=1)
    tone: str = Field(...)
    provider: Literal["claude", "openai"] = Field("claude")


class GenerateResponse(BaseModel):
    email: str
    provider: str
    model: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    try:
        email = generate_email(
            intent=req.intent,
            key_facts=req.key_facts,
            tone=req.tone,
            provider=req.provider,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    model_env = "CLAUDE_MODEL" if req.provider == "claude" else "OPENAI_MODEL"
    default = "claude-haiku-4-5" if req.provider == "claude" else "gpt-4o-mini"
    return GenerateResponse(
        email=email,
        provider=req.provider,
        model=os.environ.get(model_env, default),
    )
