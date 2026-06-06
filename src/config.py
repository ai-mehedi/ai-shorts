"""Shared config + path helpers."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | Path = "config.yaml") -> dict:
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def job_dir(cfg: dict, job_id: str) -> Path:
    d = ROOT / cfg["paths"]["output_dir"] / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def models_dir(cfg: dict) -> Path:
    d = ROOT / cfg["paths"]["models_dir"]
    d.mkdir(parents=True, exist_ok=True)
    # so HF / torch caches land on the (RunPod network) volume
    os.environ.setdefault("HF_HOME", str(d / "hf"))
    return d
