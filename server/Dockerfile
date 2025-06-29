# From python:3.11-slim-bookworm AS model_downloader

# RUN apt-get update && apt-get install -y --no-install-recommends wget \
#   && rm -rf /var/lib/apt/lists/*

# ARG TEMP_DIR_ARG=/opt/downloaded_models  

# RUN mkdir -p ${TEMP_DIR_ARG} \
#   && echo "Downloading Kokoro models to ${KOKORO_MODEL_DIR}..." \
#   && wget -nv --show-progress -P ${TEMP_DIR_ARG} https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx \
#   && wget -nv --show-progress -P ${TEMP_DIR_ARG} https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin \
#   && echo "Model download complete."

# FROM python:3.11.11-slim-bookworm

FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3.12 python3-pip python3.12-venv ffmpeg espeak-ng && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ONNX_PROVIDER CUDAExecutionProvider

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# workaround for CUDAExecutionProvider not found
RUN pip uninstall -y onnxruntime onnxruntime-gpu
RUN pip install onnxruntime-gpu



COPY . .

# ARG KOKORO_MODEL_DIR_ARG=/app/app/services/kokoro
# ENV KOKORO_MODEL_DIR=${KOKORO_MODEL_DIR_ARG}

# RUN mkdir -p ${KOKORO_MODEL_DIR}
# COPY --from=model_downloader /opt/downloaded_models/ ${KOKORO_MODEL_DIR}

EXPOSE 8000