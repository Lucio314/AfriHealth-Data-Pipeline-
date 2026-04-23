import logging
from pipeline.config import get_db_connection

logger = logging.getLogger(__name__)


def upsert_country(cursor, country_code: str) -> int:
    """Insère ou récupère l'id d'un pays."""
    cursor.execute(
        """
        INSERT INTO analytics.countries (country_code, country_name)
        VALUES (%s, %s)
        ON CONFLICT (country_code) DO NOTHING
        RETURNING id
        """,
        (country_code, country_code),  # nom = code en attendant un référentiel
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "SELECT id FROM analytics.countries WHERE country_code = %s",
        (country_code,),
    )
    return cursor.fetchone()[0]


def upsert_indicator(cursor, indicator_code: str) -> int:
    """Insère ou récupère l'id d'un indicateur."""
    cursor.execute(
        """
        INSERT INTO analytics.indicators (indicator_code, indicator_name)
        VALUES (%s, %s)
        ON CONFLICT (indicator_code) DO NOTHING
        RETURNING id
        """,
        (indicator_code, indicator_code),  # nom = code, à enrichir plus tard
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "SELECT id FROM analytics.indicators WHERE indicator_code = %s",
        (indicator_code,),
    )
    return cursor.fetchone()[0]


def transform_and_load() -> int:
    """
    Lit raw.who_data, normalise, et insère dans analytics.health_data.
    Ignore les doublons (ON CONFLICT DO NOTHING sur la contrainte uniq_health_entry).
    Retourne le nombre de lignes insérées.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    total_inserted = 0

    try:
        cursor.execute(
            """
            SELECT data
            FROM raw.who_data
            WHERE data->>'SpatialDim' IS NOT NULL
              AND data->>'TimeDim' IS NOT NULL
              AND data->>'NumericValue' IS NOT NULL
            """
        )
        rows = cursor.fetchall()
        logger.info(f"[TRANSFORM] {len(rows)} records à transformer")

        for (record,) in rows:
            country_code = record.get("SpatialDim")
            indicator_code = record.get("indicator_code")
            year_raw = record.get("TimeDim")
            value_raw = record.get("NumericValue")

            # Validation minimale
            if not all([country_code, indicator_code, year_raw, value_raw]):
                continue

            try:
                year = int(year_raw)
                value = float(value_raw)
            except (ValueError, TypeError):
                logger.warning(f"[TRANSFORM] Valeur non convertible : {record}")
                continue

            country_id = upsert_country(cursor, country_code)
            indicator_id = upsert_indicator(cursor, indicator_code)

            cursor.execute(
                """
                INSERT INTO analytics.health_data (country_id, indicator_id, year, value)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT uniq_health_entry DO NOTHING
                """,
                (country_id, indicator_id, year, value),
            )
            if cursor.rowcount == 1:
                total_inserted += 1

        conn.commit()
        logger.info(f"[TRANSFORM] {total_inserted} lignes insérées en analytics.health_data")

    except Exception as e:
        conn.rollback()
        logger.error(f"[TRANSFORM] Rollback — erreur : {e}")
        raise
    finally:
        cursor.close()
        conn.close()

    return total_inserted
