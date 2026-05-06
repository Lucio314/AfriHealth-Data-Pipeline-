from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pipeline.config import get_db_connection

router = APIRouter()


class Indicator(BaseModel):
    id: int
    indicator_code: str
    indicator_name: str


@router.get("/", response_model=list[Indicator], summary="Lister tous les indicateurs")
def list_indicators():
    """Retourne la liste de tous les indicateurs présents en base."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, indicator_code, indicator_name "
            "FROM analytics.indicators ORDER BY indicator_code"
        )
        rows = cursor.fetchall()
        return [
            Indicator(id=r[0], indicator_code=r[1], indicator_name=r[2])
            for r in rows
        ]
    finally:
        cursor.close()
        conn.close()


@router.get("/{indicator_code}", response_model=Indicator, summary="Détail d'un indicateur")
def get_indicator(indicator_code: str):
    """Retourne un indicateur par son code WHO."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, indicator_code, indicator_name "
            "FROM analytics.indicators WHERE indicator_code = %s",
            (indicator_code.upper(),),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Indicateur '{indicator_code}' introuvable",
            )
        return Indicator(id=row[0], indicator_code=row[1], indicator_name=row[2])
    finally:
        cursor.close()
        conn.close()
