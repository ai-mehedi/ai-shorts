#!/usr/bin/env bash
# Start the AI Shorts Factory web GUI.
# Usage:  bash start.sh
set -e

# safety net: install deps if setup wasn't run
python -c "import gradio" >/dev/null 2>&1 || pip install -r requirements.txt

echo "============================================"
echo "  🎬 Starting AI Shorts Factory GUI..."
echo ""
echo "  Open the  *.gradio.live  link printed below"
echo "  in your browser (works from phone or PC)."
echo "============================================"
echo ""

python app.py
