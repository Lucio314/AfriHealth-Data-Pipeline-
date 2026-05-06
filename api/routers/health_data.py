from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pipeline.config import get_db_connection

router = APIRouter()


class HealthRecord(BaseModel):
    country_code: str
    indicator_code: str
    year: int
    value: float


@router.get(
    "/",
    response_model=list[HealthRecord],
    summary="Interroger les données de santé",
)
def get_health_data(
    country_code: str | None = Query(None, description="Code pays ISO 3 lettres, ex: NGA"),
    indicator_code: str | None = Query(None, description="Code indicateur WHO, ex: WHOSIS_000001"),
    year_min: int | None = Query(None, description="Année minimale (incluse)"),
    year_max: int | None = Query(None, description="Année maximale (incluse)"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de résultats"),
):
    """
    Retourne les données de santé filtrées par pays, indicateur et/ou plage d'années.
    Au moins un filtre est recommandé pour éviter des réponses trop volumineuses.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT c.country_code, i.indicator_code, hd.year, hd.value
            FROM analytics.health_data hd
            JOIN analytics.countries   c ON c.id = hd.country_id
            JOIN analytics.indicators  i ON i.id = hd.indicator_id
            WHERE 1=1
        """
        params: list = []

        if country_code:
            query += " AND c.country_code = %s"
            params.append(country_code.upper())
        if indicator_code:
            query += " AND i.indicator_code = %s"
            params.append(indicator_code.upper())
        if year_min is not None:
            query += " AND hd.year >= %s"
            params.append(year_min)
        if year_max is not None:
            query += " AND hd.year <= %s"
            params.append(year_max)

        query += " ORDER BY c.country_code, i.indicator_code, hd.year LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            HealthRecord(
                country_code=r[0],
                indicator_code=r[1],
                year=r[2],
                value=r[3],
            )
            for r in rows
        ]
    finally:
        cursor.close()
        conn.close()


@router.get(
    "/{country_code}/{indicator_code}",
    response_model=list[HealthRecord],
    summary="Série temporelle pays × indicateur",
)
def get_time_series(country_code: str, indicator_code: str):
    """
    Retourne toutes les années disponibles pour un pays et un indicateur donnés.
    Idéal pour tracer une courbe temporelle.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT c.country_code, i.indicator_code, hd.year, hd.value
            FROM analytics.health_data hd
            JOIN analytics.countries  c ON c.id = hd.country_id
            JOIN analytics.indicators i ON i.id = hd.indicator_id
            WHERE c.country_code   = %s
              AND i.indicator_code = %s
            ORDER BY hd.year
            """,
            (country_code.upper(), indicator_code.upper()),
        )
        rows = cursor.fetchall()
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune donnée pour {country_code}/{indicator_code}",
            )
        return [
            HealthRecord(
                country_code=r[0],
                indicator_code=r[1],
                year=r[2],
                value=r[3],
            )
            for r in rows
        ]
    finally:
        cursor.close()
        conn.close()
