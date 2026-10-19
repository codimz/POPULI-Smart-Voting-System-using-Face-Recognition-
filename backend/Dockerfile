# T20: Multi-stage Docker image for POPULI backend
FROM python:3.12-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Install runtime libpq (asyncpg needs it)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# App code
COPY app/ ./app/
COPY .env ./

# Default env (override via compose)
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SQL_ECHO=false
ENV DEBUG=false

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
