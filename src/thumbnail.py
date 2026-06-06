"""Step 6 — eye-catching thumbnail / cover with bold title text.

Uses a frame from the AI video as the background (or a dark fallback in
quick-test mode), then overlays the title in big bold text with an outline.
"""
import re
import textwrap
from pathlib import Path

# emoji / symbol / arrow / variation-selector ranges that the bold fonts can't draw
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002190-\U000021FF"
    "\U00002B00-\U00002BFF\U0000FE00-\U0000FE0F\U00002300-\U000023FF]"
)


def _clean_title(title: str) -> str:
    """Drop emojis/symbols so they don't render as empty boxes on the image."""
    return re.sub(r"\s+", " ", _EMOJI.sub("", title)).strip()

FONT_CANDIDATES = [
    "C:/Windows/Fonts/ariblk.ttf",   # Arial Black (Windows)
    "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold (Windows)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux/RunPod
]


def _load_font(size: int):
    from PIL import ImageFont
    for c in FONT_CANDIDATES:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def _cover(img, w, h):
    """Resize+center-crop so the image fully covers w x h."""
    from PIL import Image
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    img = img.resize((int(src_w * scale), int(src_h * scale)), Image.LANCZOS)
    x = (img.size[0] - w) // 2
    y = (img.size[1] - h) // 2
    return img.crop((x, y, x + w, y + h))


def _base_image(source, w, h):
    from PIL import Image
    img = None
    if source and Path(source).exists():
        try:
            import imageio.v3 as iio
            frame = iio.imread(str(source), index=10)  # grab a frame
            img = Image.fromarray(frame)
        except Exception:
            img = None
    if img is None:
        img = Image.new("RGB", (w, h), (12, 12, 18))  # dark fallback
    return _cover(img.convert("RGB"), w, h)


def make_thumbnail(title: str, source, out_path: Path, cfg: dict,
                   ai_prompt: str | None = None) -> Path:
    from PIL import Image, ImageDraw

    w, h = cfg["output"]["width"], cfg["output"]["height"]

    # if there's no video frame, generate a real scary image with FLUX
    have_source = source and Path(source).exists()
    if not have_source and ai_prompt and cfg.get("thumbnail", {}).get("use_ai", False):
        try:
            from . import image_gen
            bg = out_path.parent / "thumb_bg.png"
            image_gen.generate_image(ai_prompt, bg, cfg)
            source = bg
        except Exception as e:
            print(f"  [thumb] FLUX image failed ({e}); using dark background")

    base = _base_image(source, w, h).convert("RGBA")

    # darken top + bottom bands so text pops
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle([0, 0, w, int(h * 0.34)], fill=(0, 0, 0, 150))
    sd.rectangle([0, int(h * 0.80), w, h], fill=(0, 0, 0, 120))
    base = Image.alpha_composite(base, shade)

    draw = ImageDraw.Draw(base)
    font = _load_font(int(w * 0.115))
    clean = _clean_title(title).upper() or "SCARY STORY"
    lines = textwrap.wrap(clean, width=13) or [clean]

    y = int(h * 0.07)
    outline = max(3, w // 220)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        # black outline
        for dx in range(-outline, outline + 1):
            for dy in range(-outline, outline + 1):
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))
        # yellow fill (high CTR for horror)
        draw.text((x, y), line, font=font, fill=(255, 221, 0, 255))
        y += int((bbox[3] - bbox[1]) * 1.25)

    base.convert("RGB").save(out_path, quality=92)
    return out_path


if __name__ == "__main__":
    import argparse

    from .config import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--source", default=None, help="video or image for background")
    ap.add_argument("--out", default="thumbnail.jpg")
    args = ap.parse_args()
    make_thumbnail(args.title, args.source, Path(args.out), load_config())
    print("wrote", args.out)
