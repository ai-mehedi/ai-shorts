# ai-short — AI YouTube Shorts Factory 🎬

Fully automated **scary-story YouTube Shorts** for USA / Tier-1 audiences.

**Stack:** PyTorch · HunyuanVideo (AI video) · Kokoro / F5-TTS (voice) · WhisperX (captions) · FFmpeg (assembly) · RunPod (GPU).

---

## Pipeline

```
script_gen  →  tts  →  captions  →  video_gen  →  assemble  →  (upload)
   (LLM)     (voice)   (WhisperX)  (HunyuanVideo)  (FFmpeg)    (YouTube)
```

Each step is a standalone module in `src/` and can run independently.
Output: `output/<job_id>/short.mp4` at **1080×1920**.

---

## Quick start — EASY GUI mode (recommended) 🖱️

No command line needed after setup. A web page with buttons.

```bash
# 1. install (once)
pip install -r requirements.txt        # ffmpeg must also be installed
cp .env.example .env                    # add OPENAI_API_KEY (ChatGPT) or ANTHROPIC_API_KEY

# 2. start the web app
python app.py
```

Then open the link it prints in your browser. Type a topic, pick **ChatGPT**
or **Claude**, and click **🎬 Make My Short**.
Tick **Quick test** to skip the slow AI video (no big GPU needed).

On RunPod, `app.py` prints a public `share` link you can open from anywhere.

---

## Command-line mode (optional)

```bash
python -m src.pipeline --topic "abandoned hospital night shift"
python -m src.pipeline --topic "..." --skip-video      # fast test
python -m src.script_gen --topic "..." --provider openai
```

---

## Run on RunPod — just 2 commands (no code editing) 🚀

1. Start a RunPod GPU pod (A100 80GB / H100 for AI video). Use a PyTorch +
   CUDA template. Mount a **network volume at `/workspace/models`**.
2. Upload this folder (or `git clone` it), open the pod's **web terminal**, then:

```bash
bash setup.sh     # installs everything + makes .env  (run once)
nano .env         # paste your OPENAI_API_KEY, then Ctrl+O, Enter, Ctrl+X
bash start.sh     # launches the GUI
```

3. Click the **`https://xxxxx.gradio.live`** link it prints → that's your GUI,
   open it in any browser (phone or PC). Type a topic, click **Make My Short**.

💡 Tip: you can also set `OPENAI_API_KEY` as a RunPod **environment variable** in
the pod template — then `setup.sh` puts it in `.env` automatically and you can
skip the `nano .env` step.

On Windows (local), just double-click **`start.bat`** instead.

---

## GPU split (advanced)

The video step needs a big GPU. Recommended split:

| Step              | GPU            | Why                       |
|-------------------|----------------|---------------------------|
| script / tts / captions | RTX 4090 (cheap) or CPU | light                |
| **video_gen (HunyuanVideo)** | **A100 80GB / H100** | heavy VRAM     |
| assemble          | any (CPU ok)   | ffmpeg only               |

Build the container with `runpod/Dockerfile`, mount a **network volume** at
`/workspace/models` so the ~40GB of weights download only once.

See `config.yaml` to tune resolution, clip length, voice, etc.

---

## Cost (rough)

~$0.10–$0.50 per short, dominated by HunyuanVideo GPU time.
Use RunPod **Serverless** once stable to pay only per-second.

---

## Legal / safety

- Background music: use **YouTube Audio Library** or generated music — never copyrighted tracks.
- Scary stories are fiction; avoid real names / real tragedies.
- Follow YouTube's automation & disclosure policies (label AI content).
