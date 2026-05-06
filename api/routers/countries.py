from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pipeline.config import get_db_connection

router = APIRouter()


class Country(BaseModel):
    id: int
    country_code: str
    country_name: str
    region: str | None = None


@router.get("/", response_model=list[Country], summary="Lister tous les pays")
def list_countries():
    """Retourne la liste de tous les pays présents en base."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, country_code, country_name, region "
            "FROM analytics.countries ORDER BY country_code"
        )
        rows = cursor.fetchall()
        return [
            Country(id=r[0], country_code=r[1], country_name=r[2], region=r[3])
            for r in rows
        ]
    finally:
        cursor.close()
        conn.close()


@router.get("/{country_code}", response_model=Country, summary="Détail d'un pays")
def get_country(country_code: str):
    """Retourne les informations d'un pays par son code ISO 3166-1 alpha-3."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, country_code, country_name, region "
            "FROM analytics.countries WHERE country_code = %s",
            (country_code.upper(),),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Pays '{country_code}' introuvable")
        return Country(id=row[0], country_code=row[1], country_name=row[2], region=row[3])
    finally:
        cursor.close()
        conn.close()
