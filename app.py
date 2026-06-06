"""Web GUI for ai-short — no command line needed.

Run:   python app.py
Then open the link it prints (on RunPod it gives a public --share link).

One click makes: story -> viral score -> voice -> music -> captions -> AI video
-> thumbnail. Or just check the viral score first (free, no GPU).
"""
import json
import re
import time
from pathlib import Path

import gradio as gr

from src import (assemble, captions, thumbnail, topic_gen, tts, video_gen,
                 viral_score)
from src.config import job_dir, load_config, models_dir

PROVIDER_MAP = {"ChatGPT (OpenAI)": "openai", "Claude (Anthropic)": "anthropic"}
VOICES = ["am_michael", "am_adam", "af_heart", "af_bella", "bm_george"]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "short"


def surprise_topic(provider_label):
    cfg = load_config()
    try:
        return topic_gen.generate_topic(cfg, provider=PROVIDER_MAP[provider_label])
    except Exception as e:
        return f"(error: {e} — check your API key)"


def check_score(topic, provider_label):
    """Cheap: write + score a script, NO voice/video. Decide before spending GPU."""
    cfg = load_config()
    cfg["llm"]["provider"] = PROVIDER_MAP[provider_label]
    try:
        if not topic.strip():
            topic = topic_gen.generate_topic(cfg)
        script, report = viral_score.best_script(topic, cfg)
    except Exception as e:
        return f"❌ {e}\n\nAdd your API key to .env first.", ""
    story = f"📌 {script['title']}\n\n{script['narration']}\n\n👉 {script.get('cta','')}"
    return viral_score.format_report(report), story


def make_short(topic, provider_label, skip_video, target_seconds, voice):
    """Generator: yields (status, score, script, audio, video, thumb)."""
    cfg = load_config()
    cfg["llm"]["provider"] = PROVIDER_MAP[provider_label]
    cfg["output"]["target_seconds"] = int(target_seconds)
    cfg["tts"]["voice"] = voice
    models_dir(cfg)

    if not topic.strip():
        yield "🎲 Picking a viral topic...", "", "", None, None, None
        try:
            topic = topic_gen.generate_topic(cfg)
        except Exception as e:
            yield f"❌ {e}\n\nAdd your API key to .env first.", "", "", None, None, None
            return

    job_id = f"{int(time.time())}-{slugify(topic)}"
    work = job_dir(cfg, job_id)

    # 1. script + viral score (keeps the best of several tries)
    yield f"✍️ Writing & scoring stories: “{topic}”...", "", "", None, None, None
    try:
        script, report = viral_score.best_script(topic, cfg)
    except Exception as e:
        yield f"❌ Script failed: {e}\n\nDid you add your API key to .env?", "", "", None, None, None
        return
    (work / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
    (work / "viral_score.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    score_text = viral_score.format_report(report)
    script_text = f"📌 {script['title']}\n\n{script['narration']}\n\n👉 {script.get('cta','')}"
    yield f"🎯 Score {report['overall']}/100. Recording voiceover...", score_text, script_text, None, None, None

    # 2. voice
    try:
        voice_path = tts.make_voiceover(script["narration"], work / "voice.wav", cfg)
    except Exception as e:
        yield f"❌ Voice failed: {e}", score_text, script_text, None, None, None
        return
    yield "💬 Voice done. Making captions...", score_text, script_text, str(voice_path), None, None

    # 3. captions (+ opening hook card)
    hook = script.get("hook") or script["narration"].split(".")[0]
    try:
        caps = captions.make_captions(voice_path, work / "captions.ass", cfg, hook=hook)
    except Exception as e:
        yield f"❌ Captions failed: {e}", score_text, script_text, str(voice_path), None, None
        return

    thumb_prompt = script["scenes"][0]["video_prompt"] if script.get("scenes") else script["title"]

    if skip_video:
        yield "🖼️ Making AI thumbnail (FLUX)...", score_text, script_text, str(voice_path), None, None
        thumb = thumbnail.make_thumbnail(script["title"], None, work / "thumbnail.jpg", cfg, ai_prompt=thumb_prompt)
        yield (f"✅ Quick test done.\nFolder: {work}"), score_text, script_text, str(voice_path), None, str(thumb)
        return

    # 4. video
    yield "🎥 Generating AI video (HunyuanVideo — the slow part)...", score_text, script_text, str(voice_path), None, None
    try:
        scenes = video_gen.generate_all(script["scenes"], work, cfg)
    except Exception as e:
        yield (f"❌ Video failed: {e}\n\nHunyuanVideo needs a big GPU (A100/H100). "
               "Tick 'Quick test' to skip video."), score_text, script_text, str(voice_path), None, None
        return

    # 5. assemble
    yield "🧩 Mixing video + voice + music + captions...", score_text, script_text, str(voice_path), None, None
    try:
        out = assemble.assemble(scenes, voice_path, caps, work / "short.mp4", cfg)
    except Exception as e:
        yield f"❌ Assembly failed: {e}", score_text, script_text, str(voice_path), None, None
        return

    # 6. thumbnail
    thumb = thumbnail.make_thumbnail(script["title"], scenes[0], work / "thumbnail.jpg", cfg, ai_prompt=thumb_prompt)
    yield f"✅ DONE! Short + thumbnail ready.\nFolder: {work}", score_text, script_text, str(voice_path), str(out), str(thumb)


with gr.Blocks(title="AI Shorts Factory", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎬 AI Shorts Factory\n### Make viral scary YouTube Shorts with AI — one click.")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                topic = gr.Textbox(label="Story topic (leave empty = auto)", scale=4,
                                   placeholder="e.g. abandoned hospital night shift")
                dice = gr.Button("🎲", scale=1)
            provider = gr.Dropdown(list(PROVIDER_MAP.keys()), value="ChatGPT (OpenAI)", label="AI brain")
            voice = gr.Dropdown(VOICES, value="am_michael", label="Voice (am_ = American male)")
            length = gr.Slider(40, 60, value=45, step=5, label="Length (seconds)")
            skip = gr.Checkbox(label="⚡ Quick test (skip AI video — fast, no big GPU)", value=True)
            with gr.Row():
                check = gr.Button("🔍 Check Viral Score (free)")
                go = gr.Button("🎬 Make My Short", variant="primary")
        with gr.Column(scale=1):
            status = gr.Markdown("Ready. Type a topic (or leave empty) and click a button.")
            score_box = gr.Textbox(label="🎯 Viral Score", lines=12)
            script_box = gr.Textbox(label="📝 Story", lines=6)
            with gr.Row():
                audio_out = gr.Audio(label="🔊 Voiceover")
                thumb_out = gr.Image(label="🖼️ Thumbnail")
            video_out = gr.Video(label="🎬 Final Short")

    dice.click(surprise_topic, [provider], [topic])
    check.click(check_score, [topic, provider], [score_box, script_box])
    go.click(make_short, [topic, provider, skip, length, voice],
             [status, score_box, script_box, audio_out, video_out, thumb_out])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
