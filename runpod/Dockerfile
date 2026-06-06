# RunPod image for ai-short. Use a CUDA + PyTorch base.
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive \
    HF_HOME=/workspace/models/hf \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mount a RunPod NETWORK VOLUME at /workspace/models so the ~40GB of
# HunyuanVideo + WhisperX weights download only once.
VOLUME ["/workspace/models"]

CMD ["python", "-m", "src.pipeline", "--topic", "abandoned hospital night shift"]
