import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

WHO_API_BASE_URL = "https://ghoapi.azureedge.net/api"

# Indicateurs WHO ciblés (Afrique sub-saharienne prioritaire)
WHO_INDICATORS = [
    "WHOSIS_000001",  # Life expectancy at birth
    "WHOSIS_000015",  # Healthy life expectancy (HALE) at birth
    "MDG_0000000026", # Under-five mortality rate
    "NUTRITION_ANT_WHZ_NE2", # Wasting prevalence
]

# Codes pays Afrique (ISO 3166-1 alpha-3)
AFRICAN_COUNTRIES = [
    "NGA", "ETH", "COD", "TZA", "KEN",
    "UGA", "GHA", "MOZ", "MDG", "CMR",
    "CIV", "NER", "BFA", "MLI", "MWI",
    "ZMB", "SEN", "TCD", "GIN", "RWA",
    "ZAF", "DZA", "MAR", "EGY", "SDN",
]


def get_db_connection():
    """Retourne une connexion psycopg2 depuis les variables d'environnement."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "afrihealth"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
