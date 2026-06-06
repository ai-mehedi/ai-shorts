"""Viral score checker — rate a script BEFORE spending GPU on the video.

Scores the script on the retention factors that beat the YouTube swipe:
hook, curiosity gap, second hook, cliffhangers, escalation, twist/loop, pacing,
CTA. Use it to keep only the strong scripts.
"""
import json
import re

from . import script_gen
from .config import load_config

RUBRIC = """You are a brutal YouTube Shorts retention analyst. Judge this
scary-story script ONLY on whether viewers will watch to the end instead of
swiping away. Be strict — most scripts are average.

Rate each factor 0-10:
- hook_strength: does the FIRST line stop the swipe within 3 seconds?
- curiosity_gap: is there an open loop / unanswered question pulling them in?
- second_hook: is there a fresh twist/shock around the 15-second mark?
- cliffhangers: do sentences pull you to the next one?
- escalation: does tension/fear climb scene by scene?
- twist_loop: strong twist ending that loops back to the first line?
- pacing_length: tight, no filler, right length for a Short?
- cta: does it make people want to follow / watch Part 2?

Return ONLY JSON:
{
  "scores": {"hook_strength":0,"curiosity_gap":0,"second_hook":0,"cliffhangers":0,
             "escalation":0,"twist_loop":0,"pacing_length":0,"cta":0},
  "overall_0_100": 0,
  "verdict": "one short blunt sentence",
  "top_fixes": ["2-3 concrete fixes to raise the score"]
}"""

CLIFF_PHRASES = ["but then", "that's when", "what i saw", "until", "suddenly",
                 "and then", "that's why", "i realized", "too late"]


def _heuristics(script: dict, cfg: dict) -> dict:
    hook = (script.get("hook") or "").strip()
    narration = (script.get("narration") or "")
    words = len(narration.split())
    target = int(cfg["output"]["target_seconds"] * 2.5)
    low = narration.lower()
    return {
        "hook_words": len(hook.split()),
        "hook_ok": 0 < len(hook.split()) <= 10,
        "narration_words": words,
        "length_ok": abs(words - target) <= target * 0.35,
        "cliffhanger_hits": sum(low.count(p) for p in CLIFF_PHRASES),
    }


def score_script(script: dict, cfg: dict, provider: str | None = None) -> dict:
    llm = cfg.get("llm", {})
    provider = provider or llm.get("provider", "openai")
    payload = json.dumps({
        "title": script.get("title", ""),
        "hook": script.get("hook", ""),
        "narration": script.get("narration", ""),
        "cta": script.get("cta", ""),
    }, ensure_ascii=False)
    prompt = RUBRIC + "\n\nSCRIPT:\n" + payload

    if provider == "openai":
        raw = script_gen._call_openai(prompt, llm.get("openai_model", "gpt-4o"))
    else:
        raw = script_gen._call_anthropic(prompt, llm.get("anthropic_model", "claude-opus-4-8"))
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        data = json.loads(raw)
    except Exception:
        data = {"scores": {}, "overall_0_100": 0, "verdict": "could not parse", "top_fixes": []}

    scores = data.get("scores", {}) or {}
    overall = data.get("overall_0_100")
    if not overall and scores:
        overall = round(sum(scores.values()) / (len(scores) * 10) * 100)
    data["overall"] = int(overall or 0)
    data["checks"] = _heuristics(script, cfg)
    return data


def best_script(topic: str, cfg: dict, tries: int | None = None):
    """Generate several scripts, return the highest-scoring (script, report)."""
    q = cfg.get("quality", {})
    tries = tries or q.get("max_retries", 3)
    min_score = q.get("min_viral_score", 75)

    best = None
    for i in range(tries):
        script = script_gen.generate_script(topic, cfg)
        report = score_script(script, cfg)
        print(f"  [score] try {i+1}/{tries}: {report['overall']}/100")
        if best is None or report["overall"] > best[1]["overall"]:
            best = (script, report)
        if report["overall"] >= min_score:
            break
    return best


def format_report(report: dict) -> str:
    s = report.get("scores", {})
    c = report.get("checks", {})
    bars = "\n".join(
        f"  {k:<16} {'█'*int(v)}{'░'*(10-int(v))} {v}/10"
        for k, v in s.items()
    )
    grade = ("🔥 VIRAL READY" if report["overall"] >= 80 else
             "👍 GOOD" if report["overall"] >= 70 else
             "⚠️ WEAK — regenerate" if report["overall"] >= 50 else
             "❌ SWIPE BAIT — redo")
    fixes = "\n".join(f"  • {f}" for f in report.get("top_fixes", []))
    return (
        f"🎯 VIRAL SCORE: {report['overall']}/100   {grade}\n"
        f"\"{report.get('verdict','')}\"\n\n"
        f"{bars}\n\n"
        f"Checks: hook {c.get('hook_words','?')} words "
        f"({'ok' if c.get('hook_ok') else 'too long'}), "
        f"{c.get('narration_words','?')} narration words "
        f"({'ok' if c.get('length_ok') else 'off-target'}), "
        f"{c.get('cliffhanger_hits','?')} cliffhanger phrases\n\n"
        f"Top fixes:\n{fixes}"
    )


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    args = ap.parse_args()
    cfg = load_config()
    script, report = best_script(args.topic, cfg)
    print("\n" + format_report(report))
    print(f"\nChosen title: {script['title']}")
