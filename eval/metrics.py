from __future__ import annotations

import json
import os
import re

import anthropic

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-4-7")


def _ask_judge(system: str, user: str, max_tokens: int = 512) -> str:
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return next(b.text for b in resp.content if b.type == "text").strip()


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    raise ValueError(f"No JSON found in judge response: {text!r}")


# Metric 1 — Did the email include all the required facts?
FACT_RECALL_SYSTEM = """You are an email evaluator. For each fact listed, check if it appears in the email (exact or paraphrased). A fact is PRESENT if a reader would come away knowing it. It is ABSENT if it is missing or too vague.

Reply ONLY with this JSON:
{"facts": [{"fact": "<the fact>", "present": true, "evidence": "<short quote or N/A>"}]}"""


def fact_recall_score(email: str, key_facts: list[str]) -> dict:
    facts_block = "\n".join(f"- {f}" for f in key_facts)
    user = f"EMAIL:\n{email}\n\nFACTS TO CHECK:\n{facts_block}"
    raw = _ask_judge(FACT_RECALL_SYSTEM, user, max_tokens=1024)
    data = _extract_json(raw)
    per_fact = data.get("facts", [])
    present_count = sum(1 for f in per_fact if f.get("present") is True)
    score = present_count / len(key_facts) if key_facts else 0.0
    return {
        "score": round(score, 3),
        "present_count": present_count,
        "total_facts": len(key_facts),
        "per_fact": per_fact,
    }


# Metric 2 — Does the email sound like the tone the user asked for?
TONE_SYSTEM = """You are an email evaluator. Score how well the email matches the requested tone on a 1-5 scale:
5 — Perfect match.
4 — Good match, small issues.
3 — Mostly right but drifts in places.
2 — Mixed, tonally off in multiple spots.
1 — Wrong tone entirely.

Reply ONLY with this JSON:
{"rating": <1-5>, "rationale": "<one sentence>"}"""


def tone_accuracy_score(email: str, tone: str) -> dict:
    user = f"REQUESTED TONE: {tone}\n\nEMAIL:\n{email}"
    raw = _ask_judge(TONE_SYSTEM, user, max_tokens=256)
    data = _extract_json(raw)
    rating = max(1, min(5, int(data.get("rating", 1))))
    score = (rating - 1) / 4.0
    return {
        "score": round(score, 3),
        "rating": rating,
        "rationale": data.get("rationale", ""),
    }


# Metric 3 — Is the email well written and the right length?
FLUENCY_SYSTEM = """You are an email evaluator. Score how clean and concise the email is on a 1-5 scale:
5 — Tight, no filler, flows naturally.
4 — Mostly clean, minor slack.
3 — Some filler or repetition.
2 — Wordy or awkward in multiple places.
1 — Bloated or hard to follow.

Reply ONLY with this JSON:
{"rating": <1-5>, "issues": ["<short issue>", ...]}"""


def _word_count_score(email: str) -> tuple[float, int]:
    lo, hi = 80, 180
    body = re.sub(r"^\s*Subject:.*?\n", "", email, count=1, flags=re.IGNORECASE)
    wc = len(re.findall(r"\b\w+\b", body))
    if lo <= wc <= hi:
        return 1.0, wc
    if wc < lo:
        return max(0.0, 1.0 - (lo - wc) / 40.0), wc
    return max(0.0, 1.0 - (wc - hi) / 80.0), wc


def conciseness_fluency_score(email: str) -> dict:
    wc_score, wc = _word_count_score(email)
    user = f"EMAIL:\n{email}"
    raw = _ask_judge(FLUENCY_SYSTEM, user, max_tokens=256)
    data = _extract_json(raw)
    rating = max(1, min(5, int(data.get("rating", 1))))
    fluency = (rating - 1) / 4.0
    combined = 0.5 * wc_score + 0.5 * fluency
    return {
        "score": round(combined, 3),
        "word_count": wc,
        "word_count_score": round(wc_score, 3),
        "fluency_rating": rating,
        "fluency_score": round(fluency, 3),
        "issues": data.get("issues", []),
    }


METRIC_DEFINITIONS = {
    "fact_recall": {
        "description": "Did the email include all the facts the user provided?",
        "range": "0.0 to 1.0 (1.0 means all facts were included)",
    },
    "tone_accuracy": {
        "description": "Does the email sound like the tone that was requested?",
        "range": "0.0 to 1.0 (1.0 means perfect tone match)",
    },
    "conciseness_fluency": {
        "description": "Is the email well written and the right length (80-180 words)?",
        "range": "0.0 to 1.0 (1.0 means clean writing and good length)",
    },
}
