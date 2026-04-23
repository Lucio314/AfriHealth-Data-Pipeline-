-- =========================
-- SCHEMAS
-- =========================

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

-- =========================
-- RAW LAYER (données brutes)
-- =========================

CREATE TABLE IF NOT EXISTS raw.who_data (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL DEFAULT 'WHO',
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.worldbank_data (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL DEFAULT 'WORLD_BANK',
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour requêtes JSON
CREATE INDEX IF NOT EXISTS idx_who_data_json ON raw.who_data USING GIN (data);
CREATE INDEX IF NOT EXISTS idx_worldbank_data_json ON raw.worldbank_data USING GIN (data);

-- =========================
-- ANALYTICS LAYER (données propres)
-- =========================

-- Table pays
CREATE TABLE IF NOT EXISTS analytics.countries (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(10) UNIQUE NOT NULL,
    country_name TEXT NOT NULL,
    region TEXT
);

-- Table indicateurs
CREATE TABLE IF NOT EXISTS analytics.indicators (
    id SERIAL PRIMARY KEY,
    indicator_code VARCHAR(50) UNIQUE NOT NULL,
    indicator_name TEXT NOT NULL
);

-- Table principale des données de santé
CREATE TABLE IF NOT EXISTS analytics.health_data (
    id SERIAL PRIMARY KEY,
    country_id INT NOT NULL,
    indicator_id INT NOT NULL,
    year INT NOT NULL,
    value FLOAT,

    CONSTRAINT fk_country
        FOREIGN KEY(country_id)
        REFERENCES analytics.countries(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_indicator
        FOREIGN KEY(indicator_id)
        REFERENCES analytics.indicators(id)
        ON DELETE CASCADE
);

-- =========================
-- INDEXES (performance)
-- =========================

CREATE INDEX IF NOT EXISTS idx_health_country ON analytics.health_data(country_id);
CREATE INDEX IF NOT EXISTS idx_health_indicator ON analytics.health_data(indicator_id);
CREATE INDEX IF NOT EXISTS idx_health_year ON analytics.health_data(year);

-- =========================
-- CONSTRAINTS UTILES
-- =========================

-- Éviter les doublons (important)
CREATE UNIQUE INDEX IF NOT EXISTS uniq_health_entry
ON analytics.health_data(country_id, indicator_id, year);