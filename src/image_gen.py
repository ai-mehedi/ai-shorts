"""AI image generation with FLUX.1-schnell (open-source, fast, from Hugging Face).

Used to make a real scary background image for the thumbnail — so you get a
visual cover even in Quick test (no video). Needs a GPU.
"""
from pathlib import Path

import torch

_PIPE = None

STYLE = (", cinematic horror, dark, moody, photorealistic, dramatic low-key "
         "lighting, fog, 35mm film, ultra detailed, no text, no watermark")


def _get_pipe(cfg: dict):
    global _PIPE
    if _PIPE is not None:
        return _PIPE

    from diffusers import FluxPipeline

    model_id = cfg["image"]["model"]
    pipe = FluxPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()   # fit on smaller GPUs
    _PIPE = pipe
    return pipe


def generate_image(prompt: str, out_path: Path, cfg: dict, seed: int = 0) -> Path:
    img = cfg["image"]
    pipe = _get_pipe(cfg)
    gen = torch.Generator("cpu").manual_seed(seed)
    image = pipe(
        prompt + STYLE,
        width=img["width"],
        height=img["height"],
        num_inference_steps=img["steps"],
        guidance_scale=img["guidance"],
        generator=gen,
    ).images[0]
    image.save(out_path)
    return out_path


if __name__ == "__main__":
    import argparse

    from .config import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", default="image.png")
    args = ap.parse_args()
    generate_image(args.prompt, Path(args.out), load_config())
    print("wrote", args.out)
