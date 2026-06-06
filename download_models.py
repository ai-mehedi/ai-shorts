"""Pre-download the open-source models so the first run is instant.

Downloads into the HF cache on your models volume (config paths.models_dir).

    python download_models.py            # light: voice + captions (fast)
    python download_models.py --image    # + FLUX image model (~24GB)
    python download_models.py --video    # + HunyuanVideo (~40GB)
    python download_models.py --all      # everything
"""
import argparse

from src.config import load_config, models_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", action="store_true", help="FLUX image model (~24GB)")
    ap.add_argument("--video", action="store_true", help="HunyuanVideo (~40GB)")
    ap.add_argument("--all", action="store_true", help="download everything")
    args = ap.parse_args()

    cfg = load_config()
    models_dir(cfg)  # points HF_HOME at the models volume

    from huggingface_hub import snapshot_download

    print("== Kokoro voice ==")
    snapshot_download("hexgrad/Kokoro-82M")
    print("== faster-whisper (captions) ==")
    snapshot_download("Systran/faster-whisper-small")

    if args.image or args.all:
        print(f"== {cfg['image']['model']} (image, ~24GB) ==")
        snapshot_download(cfg["image"]["model"])

    if args.video or args.all:
        print(f"== {cfg['video']['model']} (video, ~40GB) ==")
        snapshot_download(cfg["video"]["model"])

    print("\n✅ models ready (cached on your volume)")


if __name__ == "__main__":
    main()
