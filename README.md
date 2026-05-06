# AfriHealth Data Pipeline

> Pipeline de données de santé publique africaines — architecture conteneurisée et orchestrée.

Projet pédagogique couvrant les fondamentaux du **Data Engineering** :
Docker Compose, Apache Airflow, FastAPI, PostgreSQL, Python.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
│                                                              │
│  ┌──────────┐    ┌────────────────────────────────────────┐  │
│  │          │    │              Apache Airflow             │  │
│  │ WHO API  │───▶│  extract → load_raw → transform (DAG)  │  │
│  │ (externe)│    └────────────────┬───────────────────────┘  │
│  └──────────┘                     │                          │
│                                   ▼                          │
│                    ┌──────────────────────────┐              │
│                    │        PostgreSQL          │              │
│                    │  ┌──────────────────────┐ │              │
│                    │  │  schema: raw          │ │              │
│                    │  │  └── who_data (JSONB) │ │              │
│                    │  ├──────────────────────┤ │              │
│                    │  │  schema: analytics   │ │              │
│                    │  │  ├── countries       │ │              │
│                    │  │  ├── indicators      │ │              │
│                    │  │  └── health_data     │ │              │
│                    │  └──────────────────────┘ │              │
│                    └──────────────┬────────────┘              │
│                                   │                          │
│                    ┌──────────────▼────────────┐              │
│                    │        FastAPI :8000        │              │
│                    │  GET /data  /countries      │              │
│                    │  GET /indicators  /health   │              │
│                    └───────────────────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

## Stack

| Composant | Rôle |
|---|---|
| **Python 3.11** | Langage principal |
| **PostgreSQL 15** | Stockage (couches raw + analytics) |
| **Apache Airflow 2.9** | Orchestration des workflows ETL |
| **FastAPI** | Exposition des données via API REST |
| **Docker Compose** | Conteneurisation et isolation des services |

---

## Structure du projet

```
AfriHealth-Data-Pipeline/
├── pipeline/                    # Package ETL principal
│   ├── config.py                # Connexion DB, indicateurs, pays
│   ├── extract/
│   │   └── who_extractor.py     # Extraction API WHO
│   ├── load/
│   │   └── raw_loader.py        # Chargement couche raw (JSONB)
│   └── transform/
│       └── who_transformer.py   # Normalisation → analytics
│
├── api/                         # Service FastAPI
│   ├── main.py                  # Application et routage
│   └── routers/
│       ├── countries.py         # GET /countries
│       ├── indicators.py        # GET /indicators
│       └── health_data.py       # GET /data
│
├── dags/
│   └── afrihealth_pipeline_dag.py  # DAG Airflow (extract→load→transform)
│
├── scripts/
│   └── create_airflow_db.sh     # Init DB Airflow au démarrage Postgres
│
├── init.sql                     # Schéma PostgreSQL (schemas raw + analytics)
├── main.py                      # Point d'entrée CLI (run manuel)
├── Dockerfile                   # Image pour le service API/pipeline
├── docker-compose.yml           # Orchestration des 5 services
├── requirements.txt             # Dépendances Python
├── Makefile                     # Commandes raccourcies
└── .env.example                 # Template des variables d'environnement
```

---

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (inclut Docker Compose v2)
- Git

> Pas besoin d'installer Python, PostgreSQL ou Airflow localement — tout tourne dans Docker.

---

## Démarrage rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/<votre-pseudo>/AfriHealth-Data-Pipeline.git
cd AfriHealth-Data-Pipeline
```

### 2. Créer le fichier d'environnement

```bash
cp .env.example .env
# Éditez .env si vous souhaitez changer les mots de passe
```

### 3. Démarrer tous les services

```bash
make up
# ou : docker compose up -d
```

Le premier démarrage prend quelques minutes (téléchargement des images, init Airflow).

### 4. Vérifier que tout est opérationnel

| Service | URL | Identifiants |
|---|---|---|
| API FastAPI (docs Swagger) | http://localhost:8000/docs | — |
| Airflow UI | http://localhost:8080 | admin / admin |
| PostgreSQL | localhost:5432 | voir `.env` |

### 5. Lancer le pipeline

**Via Airflow (recommandé)** : ouvrez http://localhost:8080, activez le DAG `afrihealth_pipeline`, puis cliquez sur "Trigger DAG".

**Via CLI (manuel)** :
```bash
make pipeline
# ou : docker compose run --rm api python main.py
```

---

## API — Endpoints disponibles

La documentation interactive est disponible sur http://localhost:8000/docs.

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/health` | Status de l'API |
| GET | `/countries` | Liste tous les pays |
| GET | `/countries/{code}` | Détail d'un pays |
| GET | `/indicators` | Liste tous les indicateurs |
| GET | `/indicators/{code}` | Détail d'un indicateur |
| GET | `/data` | Données filtrées (pays, indicateur, années) |
| GET | `/data/{country}/{indicator}` | Série temporelle |

**Exemple :**
```bash
# Espérance de vie au Nigeria depuis 2000
curl "http://localhost:8000/data/NGA/WHOSIS_000001?year_min=2000"
```

---

## Indicateurs WHO inclus

| Code | Indicateur |
|---|---|
| `WHOSIS_000001` | Life expectancy at birth |
| `WHOSIS_000015` | Healthy life expectancy (HALE) at birth |
| `MDG_0000000026` | Under-five mortality rate |
| `NUTRITION_ANT_WHZ_NE2` | Wasting prevalence |

Données couvrant 25 pays d'Afrique sub-saharienne et du Nord.

---

## Commandes utiles

```bash
make up           # Démarrer tous les services
make down         # Arrêter tous les services
make logs         # Voir les logs en temps réel
make api-logs     # Logs du service API uniquement
make airflow-logs # Logs du scheduler Airflow
make pipeline     # Lancer le pipeline manuellement
make clean        # Tout supprimer (volumes inclus — efface les données !)
make build        # Reconstruire les images Docker
```

---

## Schéma de la base de données

```
raw.who_data
  id | source | data (JSONB) | created_at

analytics.countries
  id | country_code | country_name | region

analytics.indicators
  id | indicator_code | indicator_name

analytics.health_data
  id | country_id (FK) | indicator_id (FK) | year | value
  UNIQUE (country_id, indicator_id, year)
```

---

## Pistes d'amélioration

- Ajouter un extracteur World Bank (`raw.worldbank_data` est déjà prévu en DB)
- Enrichir le référentiel pays (noms complets, régions) via un fichier de seed
- Ajouter des tests unitaires avec `pytest`
- Déployer sur un VPS avec Docker Swarm ou Kubernetes
- Intégrer un outil de visualisation (Metabase, Grafana)

---

## Licence

MIT
