FROM python:3.13.2-slim-bookworm AS model_downloader

RUN apt-get update && apt-get install -y --no-install-recommends wget \
  && rm -rf /var/lib/apt/lists/*

ARG TEMP_DIR_ARG=/opt/downloaded_models  

RUN mkdir -p ${TEMP_DIR_ARG} \
  && echo "Downloading Kokoro models to ${KOKORO_MODEL_DIR}..." \
  && wget -nv --show-progress -P ${TEMP_DIR_ARG} https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx \
  && wget -nv --show-progress -P ${TEMP_DIR_ARG} https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin \
  && echo "Model download complete."

FROM python:3.13.2-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG KOKORO_MODEL_DIR_ARG=/app/app/services/kokoro
ENV KOKORO_MODEL_DIR=${KOKORO_MODEL_DIR_ARG}

RUN mkdir -p ${KOKORO_MODEL_DIR}
COPY --from=model_downloader /opt/downloaded_models/ ${KOKORO_MODEL_DIR}

EXPOSE 8000