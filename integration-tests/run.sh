#!/usr/bin/env bash

cd "$(dirname "$0")"

export PREDS_STREAM_NAME="output-stream"
export MODEL_KEY="lin_reg.bin"

LOCAL_TAG=$(date +"%Y-%m-%d-%H-%M")
export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"

docker build -t ${LOCAL_IMAGE_NAME} ..
