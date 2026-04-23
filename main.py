import logging
from pipeline.extract.who_extractor import extract_all
from pipeline.load.raw_loader import load_raw_who
from pipeline.transform.who_transformer import transform_and_load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run():
    logger.info("=== afriHealth pipeline START ===")

    # Étape 1 — Extract
    logger.info("--- Étape 1 : Extraction WHO API ---")
    raw_data = extract_all()

    # Étape 2 — Load raw
    logger.info("--- Étape 2 : Chargement couche RAW ---")
    load_raw_who(raw_data)

    # Étape 3 — Transform & Load analytics
    logger.info("--- Étape 3 : Transformation → couche analytics ---")
    transform_and_load()

    logger.info("=== afriHealth pipeline END ===")


if __name__ == "__main__":
    run()
