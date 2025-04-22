FROM python:3.13.2-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends wget \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG KOKORO_MODEL_DIR=app/app/services/kokoro
ENV KOKORO_MODEL_DIR=$KOKORO_MODEL_DIR

RUN mkdir -p ${KOKORO_MODEL_DIR} \
  && echo "Downloading Kokoro models to ${KOKORO_MODEL_DIR}..." \
  && wget -nv --show-progress -P ${KOKORO_MODEL_DIR} https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx \
  && wget -nv --show-progress -P ${KOKORO_MODEL_DIR} https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin \
  && echo "Model download complete."

EXPOSE 8000