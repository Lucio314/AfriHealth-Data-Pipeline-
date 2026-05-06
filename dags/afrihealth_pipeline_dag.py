"""
AfriHealth Pipeline DAG
=======================
Orchestre le pipeline ETL en 3 étapes :
  1. extract  — appelle l'API WHO et récupère les données brutes
  2. load_raw — insère les données brutes en JSONB dans raw.who_data
  3. transform — normalise et charge les données dans analytics.health_data

Planification : tous les jours à 06h00 UTC (modifiable via la variable SCHEDULE).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# Paramètres du DAG
# ─────────────────────────────────────────
DEFAULT_ARGS = {
    "owner": "afrihealth",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

SCHEDULE = "0 6 * * *"  # Tous les jours à 06h00 UTC


# ─────────────────────────────────────────
# Tâches Python
# ─────────────────────────────────────────
def task_extract(**context) -> None:
    """Étape 1 — Extraction depuis l'API WHO."""
    from pipeline.extract.who_extractor import extract_all

    raw_data = extract_all()
    total = sum(len(v) for v in raw_data.values())
    logger.info(f"[DAG] Extraction terminée : {total} records au total")

    # Passe les données à la tâche suivante via XCom
    context["ti"].xcom_push(key="raw_data", value=raw_data)


def task_load_raw(**context) -> None:
    """Étape 2 — Chargement brut dans raw.who_data."""
    from pipeline.load.raw_loader import load_raw_who

    raw_data = context["ti"].xcom_pull(key="raw_data", task_ids="extract")
    if not raw_data:
        raise ValueError("[DAG] Aucune donnée reçue depuis la tâche extract")

    inserted = load_raw_who(raw_data)
    logger.info(f"[DAG] Raw load terminé : {inserted} lignes insérées")


def task_transform(**context) -> None:
    """Étape 3 — Transformation et chargement dans analytics.health_data."""
    from pipeline.transform.who_transformer import transform_and_load

    inserted = transform_and_load()
    logger.info(f"[DAG] Transform terminé : {inserted} lignes insérées en analytics")


# ─────────────────────────────────────────
# Définition du DAG
# ─────────────────────────────────────────
with DAG(
    dag_id="afrihealth_pipeline",
    description="Pipeline ETL : extraction WHO → raw → analytics",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule=SCHEDULE,
    catchup=False,
    tags=["afrihealth", "etl", "who", "health"],
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=task_extract,
    )

    load_raw = PythonOperator(
        task_id="load_raw",
        python_callable=task_load_raw,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=task_transform,
    )

    # Séquence linéaire : extract → load_raw → transform
    extract >> load_raw >> transform
