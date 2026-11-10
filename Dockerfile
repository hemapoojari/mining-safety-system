FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Install system dependencies (libgomp1 for XGBoost OpenMP support, curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user (UID 1000) for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user && \
    mkdir -p /app && \
    chown -R user:user /app

USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

# Copy application backend, ML models, simulation engine, database, and built frontend
COPY --chown=user:user backend/ ./backend/
COPY --chown=user:user ml_engine/ ./ml_engine/
COPY --chown=user:user simulation/ ./simulation/
COPY --chown=user:user frontend/dist/ ./frontend/dist/
COPY --chown=user:user mining_safety.db ./mining_safety.db

# Expose standard Hugging Face Spaces port
EXPOSE 7860

# Launch the unified FastAPI application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
