CREATE TYPE data_source_status AS ENUM ('active', 'paused', 'inactive');
CREATE TYPE discovery_status AS ENUM ('waiting', 'in_progress');

ALTER TABLE data_sources ADD COLUMN status data_source_status NOT NULL DEFAULT 'active';
UPDATE data_sources SET status = 'paused' WHERE NOT is_active;
ALTER TABLE data_sources DROP COLUMN is_active;

ALTER TABLE data_sources ADD COLUMN discovery_status discovery_status NOT NULL DEFAULT 'waiting';
UPDATE data_sources SET discovery_status = 'in_progress'
WHERE EXISTS (SELECT 1 FROM discovery_queue WHERE data_sources_id = data_sources.id);
