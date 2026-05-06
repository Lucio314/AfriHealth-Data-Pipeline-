# ─────────────────────────────────────────────────────────────────────────────
# AfriHealth Pipeline — Makefile
# Usage : make <target>
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help up down restart logs pipeline api-logs airflow-logs clean

## Affiche l'aide
help:
	@grep -E '^##' Makefile | sed 's/## //'

## Démarre tous les services (détaché)
up:
	docker compose up -d

## Arrête tous les services
down:
	docker compose down

## Redémarre tous les services
restart:
	docker compose down && docker compose up -d

## Affiche les logs de tous les services
logs:
	docker compose logs -f

## Affiche les logs de l'API uniquement
api-logs:
	docker compose logs -f api

## Affiche les logs du scheduler Airflow
airflow-logs:
	docker compose logs -f airflow-scheduler

## Lance le pipeline manuellement (hors Airflow)
pipeline:
	docker compose run --rm api python main.py

## Supprime les volumes (ATTENTION : efface toutes les données)
clean:
	docker compose down -v

## Construit les images Docker sans cache
build:
	docker compose build --no-cache
