"""Step 2 — narration voiceover. Default: Kokoro (free, deep US voice)."""
from pathlib import Path

import numpy as np
import soundfile as sf

SAMPLE_RATE = 24000


def _smooth_edges(audio: np.ndarray, sr: int) -> np.ndarray:
    """Tiny fade in/out so sentence joins don't click."""
    n = int(sr * 0.006)
    if len(audio) > 2 * n:
        fade = np.linspace(0.0, 1.0, n, dtype=np.float32)
        audio[:n] *= fade
        audio[-n:] *= fade[::-1]
    return audio


def synth_kokoro(text: str, out_path: Path, voice="am_michael", speed=0.95) -> Path:
    """Kokoro TTS -> wav. Smooth: small pause + fades between sentences."""
    from kokoro import KPipeline

    pipeline = KPipeline(lang_code="a")  # 'a' = American English
    gap = np.zeros(int(SAMPLE_RATE * 0.14), dtype=np.float32)  # natural pause
    pieces = []
    for _, _, audio in pipeline(text, voice=voice, speed=speed):
        if hasattr(audio, "detach"):
            audio = audio.detach().cpu().numpy()
        audio = np.asarray(audio, dtype=np.float32)
        pieces.append(_smooth_edges(audio, SAMPLE_RATE))
        pieces.append(gap)
    wav = np.concatenate(pieces) if pieces else np.zeros(1, dtype=np.float32)
    sf.write(out_path, wav, SAMPLE_RATE)
    return out_path


def synth_f5(text: str, out_path: Path, ref_audio: str, ref_text: str) -> Path:
    """F5-TTS voice cloning. Provide a 5-10s reference clip + its transcript."""
    from f5_tts.api import F5TTS

    f5 = F5TTS()
    wav, sr, _ = f5.infer(ref_file=ref_audio, ref_text=ref_text, gen_text=text)
    sf.write(out_path, wav, sr)
    return out_path


def make_voiceover(text: str, out_path: Path, cfg: dict) -> Path:
    t = cfg["tts"]
    if t["engine"] == "f5":
        return synth_f5(text, out_path, t["ref_audio"], t["ref_text"])
    return synth_kokoro(text, out_path, voice=t["voice"], speed=t["speed"])


if __name__ == "__main__":
    import argparse

    from .config import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", default="voice.wav")
    args = ap.parse_args()
    make_voiceover(args.text, Path(args.out), load_config())
    print("wrote", args.out)
