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

# Copy only installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application files
COPY app.py .
COPY templates ./templates
COPY static ./static

EXPOSE 5000

# Start Flask application using Gunicorn
CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:5000", "--timeout=120", "app:app"]
