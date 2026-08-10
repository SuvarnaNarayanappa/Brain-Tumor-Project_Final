#!/bin/bash

set -e

MODEL_DIR="/app/models"
MODEL_FILE="$MODEL_DIR/bt_resnet50_model.pt"

mkdir -p "$MODEL_DIR"

echo "Checking brain tumor model..."

if [ ! -f "$MODEL_FILE" ]; then
    echo "Model not found. Downloading from Azure Blob Storage..."

    python - <<'PY'
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os

account = os.environ["AZURE_STORAGE_ACCOUNT"]
container = os.environ["AZURE_STORAGE_CONTAINER"]

blob_service_client = BlobServiceClient(
    account_url=f"https://{account}.blob.core.windows.net",
    credential=DefaultAzureCredential()
)

blob_client = blob_service_client.get_blob_client(
    container=container,
    blob="models/bt_resnet50_model.pt"
)

blob_client.download_blob().readinto(
    open("/app/models/bt_resnet50_model.pt", "wb")
)

print("Model downloaded successfully.")
PY

else
    echo "Model already exists."
fi

ls -lh "$MODEL_FILE"

echo "Starting Gunicorn..."

exec gunicorn \
    --workers=2 \
    --bind=0.0.0.0:5000 \
    --timeout=120 \
    app:app
