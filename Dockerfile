# ─── Image de base ───────────────────────────────────────────────────────────
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# ─── Dépendances système minimales ────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# ─── Dépendances Python ───────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Code source ──────────────────────────────────────────────────────────────
COPY pipeline/ ./pipeline/
COPY api/      ./api/
COPY main.py   .

# ─── Exposition du port API ───────────────────────────────────────────────────
EXPOSE 8000

# ─── Commande par défaut : lancer l'API FastAPI ───────────────────────────────
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
