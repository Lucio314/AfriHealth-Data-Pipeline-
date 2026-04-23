import requests
import logging
from pipeline.config import WHO_API_BASE_URL, WHO_INDICATORS, AFRICAN_COUNTRIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def fetch_indicator(indicator_code: str, country_codes: list[str]) -> list[dict]:
    """
    Récupère les données d'un indicateur WHO pour une liste de pays.
    Retourne une liste de records bruts (dicts).
    """
    country_filter = " or ".join(
        [f"SpatialDim eq '{code}'" for code in country_codes]
    )
    url = f"{WHO_API_BASE_URL}/{indicator_code}"
    params = {
        "$filter": country_filter,
        "$select": "SpatialDim,TimeDim,NumericValue,Low,High",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        records = data.get("value", [])
        logger.info(f"[WHO] {indicator_code} → {len(records)} records récupérés")
        return records

    except requests.exceptions.Timeout:
        logger.error(f"[WHO] Timeout sur {indicator_code}")
        return []
    except requests.exceptions.HTTPError as e:
        logger.error(f"[WHO] HTTP {e.response.status_code} sur {indicator_code}")
        return []
    except Exception as e:
        logger.error(f"[WHO] Erreur inattendue sur {indicator_code}: {e}")
        return []


def extract_all() -> dict[str, list[dict]]:
    """
    Lance l'extraction pour tous les indicateurs configurés.
    Retourne un dict { indicator_code: [records] }.
    """
    results = {}
    for indicator in WHO_INDICATORS:
        records = fetch_indicator(indicator, AFRICAN_COUNTRIES)
        results[indicator] = records
    return results
