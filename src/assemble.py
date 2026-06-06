"""Step 5 — assemble final vertical short with FFmpeg.

Combines: scene clips (looped/trimmed to voice length) + voiceover
+ quiet background music + burned-in animated captions. Output 1080x1920.
"""
import subprocess
from pathlib import Path


def _duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    )
    return float(out.strip())


def _concat_scenes(scene_paths: list[Path], work: Path, cfg: dict) -> Path:
    """Concatenate scene clips into one silent video track."""
    listfile = work / "scenes.txt"
    listfile.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in scene_paths),
        encoding="utf-8",
    )
    merged = work / "merged.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c", "copy", str(merged)],
        check=True,
    )
    return merged


def assemble(scene_paths: list[Path], voice: Path, captions: Path,
             out_path: Path, cfg: dict) -> Path:
    work = out_path.parent
    o = cfg["output"]
    music = cfg["music"]

    video = _concat_scenes(scene_paths, work, cfg)
    voice_len = _duration(voice)

    # escape path for the ass filter (ffmpeg is picky on Windows)
    ass = captions.resolve().as_posix().replace(":", "\\:")

    music_path = (work.parent.parent / music["path"])
    has_music = music_path.exists()

    # filtergraph: scale+crop to 1080x1920, loop video to voice length, burn subs
    vf = (
        f"scale={o['width']}:{o['height']}:force_original_aspect_ratio=increase,"
        f"crop={o['width']}:{o['height']},"
        f"ass='{ass}'"
    )

    cmd = ["ffmpeg", "-y",
           "-stream_loop", "-1", "-i", str(video),   # 0: video (looped)
           "-i", str(voice)]                          # 1: voiceover
    if has_music:
        cmd += ["-stream_loop", "-1", "-i", str(music_path)]  # 2: music

    # loudnorm = YouTube broadcast loudness (-14 LUFS) -> clear, "loud" pro voice
    if has_music:
        afilter = (
            f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[vo];"
            f"[2:a]volume={music['volume']}[m];"
            f"[vo][m]amix=inputs=2:duration=first:dropout_transition=0[a]"
        )
    else:
        afilter = "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    cmd += ["-filter_complex", afilter, "-map", "0:v", "-map", "[a]"]

    cmd += [
        "-vf", vf,
        "-t", f"{voice_len:.2f}",
        "-r", str(cfg["video"]["fps"]),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path
