"""AI image generation for thumbnails.

Two providers (set image.provider in config.yaml):
  - openai : ChatGPT image model (gpt-image-1). Best quality, no GPU, uses your
             OpenAI key. RECOMMENDED.
  - local  : SDXL / RealVisXL on the GPU (free, but heavier).
"""
import base64
from pathlib import Path

import torch

_PIPE = None

# keep short so local SDXL's 77-token CLIP limit isn't exceeded
STYLE = ", cinematic horror movie poster, dramatic lighting, photorealistic, high detail"
NEGATIVE = "blurry, low quality, deformed, extra limbs, text, watermark, cartoon"


# ---------------- OpenAI (ChatGPT) ----------------
def _generate_openai(prompt: str, out_path: Path, cfg: dict) -> Path:
    from openai import OpenAI

    img = cfg["image"]
    client = OpenAI()
    resp = client.images.generate(
        model=img.get("openai_model", "gpt-image-1"),
        prompt=prompt + STYLE,
        size=img.get("openai_size", "1024x1536"),   # portrait
    )
    out_path.write_bytes(base64.b64decode(resp.data[0].b64_json))
    return out_path


# ---------------- Local (SDXL / RealVisXL) ----------------
def _get_pipe(cfg: dict):
    global _PIPE
    if _PIPE is not None:
        return _PIPE

    from diffusers import AutoPipelineForText2Image

    model_id = cfg["image"]["model"]
    dtype = torch.bfloat16 if "flux" in model_id.lower() else torch.float16
    pipe = AutoPipelineForText2Image.from_pretrained(model_id, torch_dtype=dtype)
    pipe = pipe.to("cuda")            # A100 has plenty of VRAM; avoids offload dtype bugs
    _PIPE = pipe
    return pipe


def _generate_local(prompt: str, out_path: Path, cfg: dict, seed: int = 0) -> Path:
    img = cfg["image"]
    pipe = _get_pipe(cfg)
    gen = torch.Generator("cuda").manual_seed(seed)
    kwargs = dict(
        prompt=prompt + STYLE,
        width=img["width"], height=img["height"],
        num_inference_steps=img["steps"], guidance_scale=img["guidance"],
        generator=gen,
    )
    if img["guidance"] > 0:
        kwargs["negative_prompt"] = NEGATIVE
    pipe(**kwargs).images[0].save(out_path)
    return out_path


def generate_image(prompt: str, out_path: Path, cfg: dict, seed: int = 0) -> Path:
    if cfg["image"].get("provider", "openai") == "openai":
        return _generate_openai(prompt, out_path, cfg)
    return _generate_local(prompt, out_path, cfg, seed)


if __name__ == "__main__":
    import argparse

    from .config import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", default="image.png")
    args = ap.parse_args()
    generate_image(args.prompt, Path(args.out), load_config())
    print("wrote", args.out)
