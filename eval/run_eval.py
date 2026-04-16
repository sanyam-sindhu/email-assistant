from __future__ import annotations

import csv
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from app.generator import generate_email
from eval.metrics import (
    METRIC_DEFINITIONS,
    conciseness_fluency_score,
    fact_recall_score,
    tone_accuracy_score,
)
from eval.scenarios import SCENARIOS

load_dotenv()

PROVIDERS = ("claude", "openai")
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
GENERATED_DIR = RESULTS_DIR / "generated"


def provider_model(provider: str) -> str:
    if provider == "claude":
        return os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def evaluate_one(provider: str, scenario) -> dict:
    print(f"  [{provider:6s}] {scenario.id} — generating...", flush=True)
    email = generate_email(
        intent=scenario.intent,
        key_facts=list(scenario.key_facts),
        tone=scenario.tone,
        provider=provider,
    )

    out_dir = GENERATED_DIR / provider
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{scenario.id}.txt").write_text(email, encoding="utf-8")

    print(f"  [{provider:6s}] {scenario.id} — scoring (3 metrics)...", flush=True)
    fact = fact_recall_score(email, list(scenario.key_facts))
    tone = tone_accuracy_score(email, scenario.tone)
    fluency = conciseness_fluency_score(email)

    return {
        "scenario_id": scenario.id,
        "provider": provider,
        "model": provider_model(provider),
        "tone": scenario.tone,
        "email": email,
        "metrics": {
            "fact_recall": fact,
            "tone_accuracy": tone,
            "conciseness_fluency": fluency,
        },
    }


def average(rows: list[dict], provider: str, metric: str) -> float:
    scores = [r["metrics"][metric]["score"] for r in rows if r["provider"] == provider]
    return round(sum(scores) / len(scores), 3) if scores else 0.0


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    started = time.time()
    all_rows: list[dict] = []

    for provider in PROVIDERS:
        print(f"\n=== Provider: {provider} ({provider_model(provider)}) ===")
        for scenario in SCENARIOS:
            try:
                row = evaluate_one(provider, scenario)
            except Exception as exc:
                print(f"  !! {scenario.id} failed: {exc}", flush=True)
                row = {
                    "scenario_id": scenario.id,
                    "provider": provider,
                    "model": provider_model(provider),
                    "tone": scenario.tone,
                    "email": "",
                    "error": str(exc),
                    "metrics": {
                        "fact_recall": {"score": 0.0},
                        "tone_accuracy": {"score": 0.0},
                        "conciseness_fluency": {"score": 0.0},
                    },
                }
            all_rows.append(row)

    raw_json_path = RESULTS_DIR / "raw_results.json"
    raw_json_path.write_text(json.dumps(all_rows, indent=2), encoding="utf-8")

    csv_path = RESULTS_DIR / "raw_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "scenario_id", "provider", "model", "tone",
            "fact_recall", "tone_accuracy", "conciseness_fluency",
            "word_count", "fluency_rating", "tone_rating",
        ])
        for r in all_rows:
            m = r["metrics"]
            writer.writerow([
                r["scenario_id"], r["provider"], r["model"], r["tone"],
                m["fact_recall"]["score"],
                m["tone_accuracy"]["score"],
                m["conciseness_fluency"]["score"],
                m["conciseness_fluency"].get("word_count", ""),
                m["conciseness_fluency"].get("fluency_rating", ""),
                m["tone_accuracy"].get("rating", ""),
            ])

    summary = {
        "metric_definitions": METRIC_DEFINITIONS,
        "judge_model": os.environ.get("JUDGE_MODEL", "claude-opus-4-7"),
        "num_scenarios": len(SCENARIOS),
        "providers": {},
    }
    for provider in PROVIDERS:
        summary["providers"][provider] = {
            "model": provider_model(provider),
            "avg_fact_recall": average(all_rows, provider, "fact_recall"),
            "avg_tone_accuracy": average(all_rows, provider, "tone_accuracy"),
            "avg_conciseness_fluency": average(all_rows, provider, "conciseness_fluency"),
        }
        metrics = summary["providers"][provider]
        metrics["avg_overall"] = round(
            (metrics["avg_fact_recall"] + metrics["avg_tone_accuracy"] + metrics["avg_conciseness_fluency"]) / 3,
            3,
        )

    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    elapsed = time.time() - started
    print(f"\n=== Done in {elapsed:.1f}s ===")
    print(f"Raw JSON : {raw_json_path}")
    print(f"Raw CSV  : {csv_path}")
    print(f"Summary  : {summary_path}")
    print("\nPer-provider averages:")
    header = f"  {'provider':8s}  {'model':22s}  {'fact':>6s}  {'tone':>6s}  {'flu.':>6s}  {'avg':>6s}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for provider in PROVIDERS:
        p = summary["providers"][provider]
        print(
            f"  {provider:8s}  {p['model']:22s}  "
            f"{p['avg_fact_recall']:6.3f}  {p['avg_tone_accuracy']:6.3f}  "
            f"{p['avg_conciseness_fluency']:6.3f}  {p['avg_overall']:6.3f}"
        )


if __name__ == "__main__":
    main()
