"""AI image generation for thumbnails (open-source, from Hugging Face).

Default model: stabilityai/sdxl-turbo — open, NO login needed, fast on a GPU.
Works with any text-to-image model via diffusers' AutoPipeline, so you can switch
to SDXL base or FLUX (FLUX needs an HF token + license acceptance) in config.yaml.
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

    from diffusers import AutoPipelineForText2Image

    model_id = cfg["image"]["model"]
    dtype = torch.bfloat16 if "flux" in model_id.lower() else torch.float16
    pipe = AutoPipelineForText2Image.from_pretrained(model_id, torch_dtype=dtype)
    pipe.enable_model_cpu_offload()   # fit comfortably on the A100
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
