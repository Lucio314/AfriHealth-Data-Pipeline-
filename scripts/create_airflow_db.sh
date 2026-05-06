#!/bin/bash
# Ce script est exécuté au premier démarrage du conteneur PostgreSQL.
# Il crée la base de données dédiée à Airflow en plus de la base pipeline.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE airflow;
    GRANT ALL PRIVILEGES ON DATABASE airflow TO $POSTGRES_USER;
EOSQL

echo "Base 'airflow' créée avec succès."
