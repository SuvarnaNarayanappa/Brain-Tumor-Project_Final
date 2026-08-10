# =========================
# Stage 1: Builder
# =========================
FROM python:3.10-slim AS builder

WORKDIR /build

COPY requirements.txt .

# Install CPU-only PyTorch
RUN pip install --no-cache-dir --prefix=/install \
    torch==2.3.1+cpu \
    torchvision==0.18.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install application dependencies
RUN pip install --no-cache-dir --prefix=/install \
    -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.10-slim

WORKDIR /app

# Install Azure CLI dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        lsb-release && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages
COPY --from=builder /install /usr/local

# Copy application files
COPY app.py .
COPY templates ./templates
COPY static ./static
COPY start.sh .

RUN chmod +x start.sh

# Model location
ENV MODEL_PATH=/app/models/bt_resnet50_model.pt

EXPOSE 5000

CMD ["./start.sh"]
