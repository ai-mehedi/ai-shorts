"""Step 4 — AI video clips per scene with HunyuanVideo (diffusers).

Heavy: run on A100 80GB / H100. CPU offload lets it fit on ~24-48GB cards.
"""
from pathlib import Path

import torch

_PIPE = None


def _get_pipe(cfg: dict):
    global _PIPE
    if _PIPE is not None:
        return _PIPE

    from diffusers import HunyuanVideoPipeline, HunyuanVideoTransformer3DModel

    model_id = cfg["video"]["model"]
    transformer = HunyuanVideoTransformer3DModel.from_pretrained(
        model_id, subfolder="transformer", torch_dtype=torch.bfloat16
    )
    pipe = HunyuanVideoPipeline.from_pretrained(
        model_id, transformer=transformer, torch_dtype=torch.float16
    )
    # fit on smaller GPUs:
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_tiling()
    _PIPE = pipe
    return pipe


def generate_scene(prompt: str, out_path: Path, cfg: dict, seed: int = 0) -> Path:
    from diffusers.utils import export_to_video

    v = cfg["video"]
    pipe = _get_pipe(cfg)
    gen = torch.Generator("cpu").manual_seed(seed)

    style = " cinematic, photorealistic, horror film lighting, fog, 35mm, high detail"
    frames = pipe(
        prompt=prompt + style,
        height=v["height"],
        width=v["width"],
        num_frames=v["frames_per_scene"],
        num_inference_steps=v["steps"],
        guidance_scale=v["guidance"],
        generator=gen,
    ).frames[0]

    export_to_video(frames, str(out_path), fps=v["fps"])
    return out_path


def generate_all(scenes: list[dict], out_dir: Path, cfg: dict) -> list[Path]:
    paths = []
    for i, scene in enumerate(scenes):
        p = out_dir / f"scene_{i:02d}.mp4"
        print(f"  [video] scene {i+1}/{len(scenes)}: {scene['video_prompt'][:60]}...")
        generate_scene(scene["video_prompt"], p, cfg, seed=i)
        paths.append(p)
    return paths


if __name__ == "__main__":
    import argparse

    from .config import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", default="scene.mp4")
    args = ap.parse_args()
    generate_scene(args.prompt, Path(args.out), load_config())
    print("wrote", args.out)
