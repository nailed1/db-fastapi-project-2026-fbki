-- =============================================================================
-- Migration 004: Hotel coordinates for OpenStreetMap
-- =============================================================================

ALTER TABLE hotels ADD COLUMN IF NOT EXISTS latitude  NUMERIC(9, 6);
ALTER TABLE hotels ADD COLUMN IF NOT EXISTS longitude NUMERIC(9, 6);

UPDATE hotels SET latitude = 55.755825, longitude = 37.617298 WHERE name = 'Гранд Отель Центр';
UPDATE hotels SET latitude = 55.972642, longitude = 37.414981 WHERE name = 'Бизнес Отель Аэропорт';
UPDATE hotels SET latitude = 43.599237, longitude = 39.725685 WHERE name = 'Отель у Моря';
