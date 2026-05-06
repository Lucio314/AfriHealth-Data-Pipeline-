from fastapi import FastAPI
from api.routers import countries, indicators, health_data

app = FastAPI(
    title="AfriHealth API",
    description=(
        "API REST pour explorer les données de santé publique africaines. "
        "Données sources : OMS (WHO Global Health Observatory)."
    ),
    version="1.0.0",
    contact={"name": "AfriHealth Pipeline"},
    license_info={"name": "MIT"},
)

app.include_router(countries.router,    prefix="/countries",  tags=["Pays"])
app.include_router(indicators.router,   prefix="/indicators", tags=["Indicateurs"])
app.include_router(health_data.router,  prefix="/data",       tags=["Données de santé"])


@app.get("/health", tags=["Status"])
def health_check():
    """Vérifie que l'API est opérationnelle."""
    return {"status": "ok", "service": "afrihealth-api"}
