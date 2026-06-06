#!/usr/bin/env bash
# One-time setup for ai-short on RunPod (or any Linux box).
# Usage:  bash setup.sh
set -e

echo "============================================"
echo "  ai-short — setup"
echo "============================================"

# --- 1. system dependencies (ffmpeg + fonts) ---
if command -v apt-get >/dev/null 2>&1; then
  echo "==> installing ffmpeg, git, fonts, espeak-ng..."
  apt-get update -y
  apt-get install -y --no-install-recommends ffmpeg git fonts-dejavu-core espeak-ng
fi

# --- 2. python packages ---
echo "==> installing python packages (this can take a few minutes)..."
pip install --upgrade pip
pip install -r requirements.txt

# Some RunPod images ship a flash-attn build that crashes diffusers on import
# ("infer_schema ... Parameter q has unsupported type"). diffusers works fine
# without it (uses PyTorch SDPA), so remove the broken build.
echo "==> removing incompatible flash-attn (if present)..."
pip uninstall -y flash-attn flash_attn >/dev/null 2>&1 || true

# --- 3. .env (API keys) ---
if [ ! -f .env ]; then
  cp .env.example .env
  # if you set keys as RunPod environment variables, they get copied in:
  [ -n "$OPENAI_API_KEY" ]    && sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|" .env
  [ -n "$ANTHROPIC_API_KEY" ] && sed -i "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY|" .env
  echo "==> created .env"
fi

# --- 4. folders (models go on the RunPod network volume) ---
mkdir -p models output assets/music

# --- 5. check the API key is set ---
if grep -qE '^(OPENAI|ANTHROPIC)_API_KEY=sk-' .env; then
  echo "==> API key detected in .env"
else
  echo ""
  echo "  ⚠️  No API key yet. Open .env and paste your key, e.g.:"
  echo "      nano .env"
  echo "      OPENAI_API_KEY=sk-...."
fi

# --- 6. pre-download models so the first run is instant ---
echo "==> downloading voice + caption models (light)..."
python download_models.py || echo "  (model pre-download skipped — will download on first run)"

echo ""
echo "============================================"
echo "  ✅ Setup done!"
echo ""
echo "  To pre-download the big AI models (recommended on A100):"
echo "     python download_models.py --all     # FLUX (~24GB) + HunyuanVideo (~40GB)"
echo ""
echo "  Then start the app:   bash start.sh"
echo "============================================"
