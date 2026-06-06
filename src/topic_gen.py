"""Auto-generate viral scary-story topics so you never run out of ideas."""
import json
import re

from . import script_gen
from .config import load_config

TOPIC_PROMPT = """Give me {n} ORIGINAL viral YouTube Shorts SCARY STORY topics for a US audience.
Rules:
- Each is a short creepy premise, max 10 words. No numbering, no quotes.
- Modern, relatable American settings (night shift, rideshare, smart home,
  babysitting, gas station, apartment hallway, road trip, delivery driver).
- Must spark instant curiosity / dread.
Return ONLY a JSON array of strings."""


def generate_topics(cfg: dict, n: int = 5, provider: str | None = None) -> list[str]:
    llm = cfg.get("llm", {})
    provider = provider or llm.get("provider", "openai")
    prompt = TOPIC_PROMPT.format(n=n)

    if provider == "openai":
        raw = script_gen._call_openai(prompt, llm.get("openai_model", "gpt-4o"))
    else:
        raw = script_gen._call_anthropic(prompt, llm.get("anthropic_model", "claude-opus-4-8"))

    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        topics = json.loads(raw)
        if isinstance(topics, list):
            return [str(t).strip() for t in topics][:n]
    except Exception:
        pass
    # fallback: split lines
    return [re.sub(r"^[\d\.\-\*\s]+", "", l).strip()
            for l in raw.splitlines() if l.strip()][:n]


def generate_topic(cfg: dict, provider: str | None = None) -> str:
    topics = generate_topics(cfg, n=1, provider=provider)
    return topics[0] if topics else "the last house on the street"


if __name__ == "__main__":
    cfg = load_config()
    for t in generate_topics(cfg, 5):
        print("-", t)
