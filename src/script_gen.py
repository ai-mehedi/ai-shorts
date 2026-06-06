"""Step 1 — generate a scary story script + per-scene video prompts.

Supports both ChatGPT (OpenAI) and Claude (Anthropic). Pick in config.yaml
(llm.provider) or pass provider= directly.
"""
import argparse
import json
import re

from .config import ROOT, load_config


def _word_count(target_seconds: int) -> int:
    # ~2.5 spoken words/sec is a comfortable Shorts pace
    return int(target_seconds * 2.5)


def _build_prompt(topic: str, cfg: dict) -> str:
    from .niches import get as get_niche

    target = cfg["output"]["target_seconds"]
    words = _word_count(target)
    num_scenes = max(3, target // 6)   # ~1 scene per 6s
    niche = get_niche(cfg.get("niche", "ai_horror"))

    template = (ROOT / "prompts" / "story.txt").read_text(encoding="utf-8")
    return template.format(
        topic=topic,
        word_count=words,
        num_scenes=num_scenes,
        niche_label=niche["label"],
        niche_guide=niche["guide"],
        visuals=niche["visuals"],
        thumbnail_style=niche["thumb"],
        payoff=niche["payoff"],
    )


def _call_openai(prompt: str, model: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


def _call_anthropic(prompt: str, model: str) -> str:
    from anthropic import Anthropic

    client = Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def generate_script(topic: str, cfg: dict, provider: str | None = None) -> dict:
    llm = cfg.get("llm", {})
    provider = provider or llm.get("provider", "openai")
    prompt = _build_prompt(topic, cfg)

    if provider == "openai":
        raw = _call_openai(prompt, llm.get("openai_model", "gpt-4o"))
    else:
        raw = _call_anthropic(prompt, llm.get("anthropic_model", "claude-opus-4-8"))

    # be forgiving if the model wraps JSON in ```json fences
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--provider", choices=["openai", "anthropic"], default=None)
    args = ap.parse_args()
    cfg = load_config()
    script = generate_script(args.topic, cfg, provider=args.provider)
    print(json.dumps(script, indent=2, ensure_ascii=False))
