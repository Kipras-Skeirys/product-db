ALTER TABLE product_queue ALTER COLUMN last_raw_ingestions_id DROP DEFAULT;
ALTER TABLE product_queue ALTER COLUMN last_raw_ingestions_id DROP NOT NULL;
DROP SEQUENCE product_queue_last_raw_ingestions_id_seq;

ALTER TABLE discovery_queue ADD COLUMN claimed_by TEXT;
ALTER TABLE discovery_queue ADD COLUMN attempt_count SMALLINT NOT NULL DEFAULT 0;

ALTER TABLE data_sources ADD COLUMN base_url TEXT;
ALTER TABLE data_sources ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;
ALTER TABLE data_sources ADD COLUMN consecutive_failures SMALLINT NOT NULL DEFAULT 0;
