ALTER TABLE data_sources ADD COLUMN rate_limit_ms INTEGER NOT NULL DEFAULT 1000;
ALTER TABLE data_sources ADD COLUMN discovery_interval INTERVAL NOT NULL DEFAULT INTERVAL '7 days';
ALTER TABLE data_sources ADD COLUMN next_discovery_due TIMESTAMPTZ NOT NULL DEFAULT now();

ALTER TABLE data_sources ADD COLUMN discovery_bot_adapter TEXT NOT NULL DEFAULT 'unassigned';
ALTER TABLE data_sources ALTER COLUMN discovery_bot_adapter DROP DEFAULT;
ALTER TABLE data_sources ADD COLUMN data_bot_adapter TEXT NOT NULL DEFAULT 'unassigned';
ALTER TABLE data_sources ALTER COLUMN data_bot_adapter DROP DEFAULT;

CREATE TYPE discovery_queue_status AS ENUM ('pending', 'in_progress');

CREATE TABLE discovery_queue (
  id BIGSERIAL PRIMARY KEY,
  data_sources_id UUID NOT NULL REFERENCES data_sources(id),
  context JSONB NOT NULL,
  status discovery_queue_status NOT NULL DEFAULT 'pending',
  claimed_at TIMESTAMPTZ
);
