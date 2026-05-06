import json
import logging
from pipeline.config import get_db_connection

logger = logging.getLogger(__name__)


def load_raw_who(extracted_data: dict[str, list[dict]]) -> int:
    """
    Insère les données brutes dans raw.who_data.
    Chaque record est stocké tel quel en JSONB avec le code indicateur.
    Retourne le nombre total de lignes insérées.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    total_inserted = 0

    try:
        for indicator_code, records in extracted_data.items():
            if not records:
                logger.warning(f"[RAW LOAD] Aucun record pour {indicator_code}, skip")
                continue

            inserted = 0
            for record in records:
                payload = json.dumps({**record, "indicator_code": indicator_code})
                cursor.execute(
                    "INSERT INTO raw.who_data (data) VALUES (%s::jsonb)",
                    (payload,),
                )
                # cursor.rowcount vaut 1 après un INSERT unitaire — comptage fiable
                inserted += cursor.rowcount

            total_inserted += inserted
            logger.info(f"[RAW LOAD] {indicator_code} → {inserted} lignes insérées")

        conn.commit()
        logger.info(f"[RAW LOAD] Total : {total_inserted} lignes en raw.who_data")

    except Exception as e:
        conn.rollback()
        logger.error(f"[RAW LOAD] Rollback — erreur : {e}")
        raise
    finally:
        cursor.close()
        conn.close()

    return total_inserted
