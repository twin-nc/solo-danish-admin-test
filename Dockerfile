FROM python:3.12-slim

# Create non-root user
RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

WORKDIR /app

# Install dependencies before copying source for layer-cache efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source with correct ownership
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini .
COPY --chown=appuser:appgroup app/ ./app/

USER appuser

EXPOSE 8000

# Run migrations then start the server (no --reload in production)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]