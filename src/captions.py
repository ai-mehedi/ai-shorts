"""Step 3 — word-level captions with WhisperX, rendered as animated ASS subs.

Also burns a big opening HOOK card (first ~2.5s) — a visual pattern-interrupt
that stops the swipe before the brain decides to leave.
"""
import textwrap
from pathlib import Path

import torch


def transcribe_words(audio_path: Path, model_name="large-v3") -> list[dict]:
    """Return [{word, start, end}, ...] using faster-whisper (word timestamps).

    faster-whisper is light and has no pyannote/numpy-2 dependency, so it works
    reliably with the torch 2.4 + numpy<2 stack on RunPod.
    """
    from faster_whisper import WhisperModel

    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute = "float16" if device == "cuda" else "int8"

    model = WhisperModel(model_name, device=device, compute_type=compute)
    segments, _ = model.transcribe(str(audio_path), word_timestamps=True, beam_size=5)

    words = []
    for seg in segments:
        for w in (seg.words or []):
            if w.start is not None and w.end is not None:
                words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    return words


def _ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    cs = int((t - int(t)) * 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass(words: list[dict], out_path: Path, cfg: dict, hook: str | None = None) -> Path:
    """CapCut-style: 3-4 words on screen, current word highlighted.

    hook: optional big text shown at the top for the first 2.5s.
    """
    c = cfg["captions"]
    res_w, res_h = cfg["output"]["width"], cfg["output"]["height"]

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {res_w}
PlayResY: {res_h}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,{c['font']},{c['font_size']},{c['primary_color']},&H00000000,&H80000000,-1,1,{c['outline']},1,2,40,40,{c['margin_v']},1
Style: Hook,{c['font']},{int(c['font_size']*1.5)},{c['highlight_color']},&H00000000,&H64000000,-1,1,{c['outline']+1},2,8,60,60,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = []

    # --- opening HOOK card (top, big, first 2.5s) — the swipe-stopper ---
    if hook:
        wrapped = "\\N".join(textwrap.wrap(hook.upper(), width=16))
        lines.append(
            f"Dialogue: 1,{_ts(0.0)},{_ts(2.5)},Hook,,0,0,0,,{{\\fad(150,250)}}{wrapped}"
        )
    group = 3  # words shown together
    for i in range(0, len(words), group):
        chunk = words[i:i + group]
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        # highlight each word as it's spoken via timed color override
        for j, w in enumerate(chunk):
            parts = []
            for k, ww in enumerate(chunk):
                if k == j:
                    parts.append(f"{{\\c{c['highlight_color']}}}{ww['word'].upper()}{{\\c{c['primary_color']}}}")
                else:
                    parts.append(ww["word"].upper())
            text = " ".join(parts)
            lines.append(
                f"Dialogue: 0,{_ts(w['start'])},{_ts(w['end'])},Base,,0,0,0,,{text}"
            )
        # keep last word visible until chunk end
        _ = start, end

    out_path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def make_captions(audio_path: Path, out_path: Path, cfg: dict, hook: str | None = None) -> Path:
    words = transcribe_words(audio_path, cfg["captions"]["whisper_model"])
    return build_ass(words, out_path, cfg, hook=hook)


if __name__ == "__main__":
    import argparse

    from .config import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", default="captions.ass")
    args = ap.parse_args()
    make_captions(Path(args.audio), Path(args.out), load_config())
    print("wrote", args.out)
