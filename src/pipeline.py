"""Orchestrator — runs the full short pipeline end to end.

    python -m src.pipeline --topic "the basement door"
    python -m src.pipeline --topic "..." --skip-video   # cheap dry run
"""
import argparse
import json
import re
import time
from pathlib import Path

from . import (assemble, captions, thumbnail, topic_gen, tts, video_gen,
               viral_score)
from .config import job_dir, load_config, models_dir


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


def run(topic: str, cfg: dict, skip_video=False) -> Path:
    models_dir(cfg)

    # 0. auto-pick a viral topic if none given
    if not topic or topic.lower() in ("auto", "surprise", "random"):
        topic = topic_gen.generate_topic(cfg)
        print(f"[0] auto topic: {topic}")

    job_id = f"{int(time.time())}-{slugify(topic)}"
    work = job_dir(cfg, job_id)
    print(f"\n=== JOB {job_id} ===")

    # 1. script — generate several, keep the highest viral score
    print("[1/6] writing + scoring scripts...")
    script, report = viral_score.best_script(topic, cfg)
    (work / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
    (work / "viral_score.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    narration = script["narration"]
    print(f"      title: {script['title']}")
    print(viral_score.format_report(report))

    # 2. voiceover
    print("[2/6] voiceover...")
    voice = tts.make_voiceover(narration, work / "voice.wav", cfg)

    # 3. captions (+ opening hook card)
    print("[3/6] captions...")
    hook = script.get("hook") or narration.split(".")[0]
    caps = captions.make_captions(voice, work / "captions.ass", cfg, hook=hook)

    thumb_prompt = (script.get("thumbnail_prompt")
                    or (script["scenes"][0]["video_prompt"] if script.get("scenes") else script["title"]))

    # 4. video
    if skip_video:
        print("[4/6] SKIPPED video")
        thumbnail.make_thumbnail(script["title"], None, work / "thumbnail.jpg", cfg, ai_prompt=thumb_prompt)
        print(f"\n✅ Quick test done -> {work}")
        return work
    print("[4/6] AI video (HunyuanVideo)...")
    scenes = video_gen.generate_all(script["scenes"], work, cfg)

    # 5. assemble
    print("[5/6] assembling final short...")
    out = assemble.assemble(scenes, voice, caps, work / "short.mp4", cfg)

    # 6. thumbnail
    print("[6/6] thumbnail...")
    thumbnail.make_thumbnail(script["title"], scenes[0], work / "thumbnail.jpg", cfg, ai_prompt=thumb_prompt)

    print(f"\n✅ DONE -> {out}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--niche", default="ai_horror", help="see src/niches.py")
    ap.add_argument("--skip-video", action="store_true",
                    help="run script+voice+captions only (no big GPU needed)")
    args = ap.parse_args()
    cfg = load_config()
    cfg["niche"] = args.niche
    run(args.topic, cfg, skip_video=args.skip_video)
