CREATE TYPE data_source_status AS ENUM ('active', 'paused', 'inactive');
CREATE TYPE discovery_status AS ENUM ('waiting', 'in_progress');

CREATE TABLE data_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  rate_limit_ms INTEGER NOT NULL DEFAULT 1000,
  discovery_interval INTERVAL NOT NULL DEFAULT INTERVAL '7 days',
  next_discovery_due TIMESTAMPTZ NOT NULL DEFAULT now(),
  discovery_bot_adapter TEXT NOT NULL,
  data_bot_adapter TEXT NOT NULL,
  base_url TEXT,
  consecutive_failures SMALLINT NOT NULL DEFAULT 0,
  status data_source_status NOT NULL DEFAULT 'active',
  discovery_status discovery_status NOT NULL DEFAULT 'waiting'
);

CREATE TABLE raw_ingestions (
  id BIGSERIAL PRIMARY KEY,
  data_sources_id UUID REFERENCES data_sources(id),
  ingested_at TIMESTAMPTZ DEFAULT now(),
  img_url TEXT,
  payload JSONB NOT NULL,
  ingested_by TEXT
);

CREATE TYPE discovery_queue_status AS ENUM ('pending', 'in_progress');

CREATE TABLE discovery_queue (
  id BIGSERIAL PRIMARY KEY,
  data_sources_id UUID NOT NULL REFERENCES data_sources(id),
  context JSONB NOT NULL,
  status discovery_queue_status NOT NULL DEFAULT 'pending',
  claimed_at TIMESTAMPTZ,
  claimed_by TEXT,
  attempt_count SMALLINT NOT NULL DEFAULT 0
);

CREATE TYPE product_queue_status AS ENUM ('waiting', 'in_progress', 'paused');

CREATE TABLE product_queue (
  id BIGSERIAL PRIMARY KEY,
  data_sources_id UUID NOT NULL REFERENCES data_sources(id),
  last_raw_ingestions_id BIGINT REFERENCES raw_ingestions(id),
  product_url TEXT NOT NULL UNIQUE,
  next_ingestion_due TIMESTAMPTZ NOT NULL DEFAULT now(),
  status product_queue_status NOT NULL DEFAULT 'waiting',
  claimed_at TIMESTAMPTZ,
  claimed_by TEXT,
  attempt_count SMALLINT NOT NULL DEFAULT 0,
  attempt_logs JSONB DEFAULT '[]'::jsonb,
  context JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE product_queue_dead_letter (
  id BIGSERIAL PRIMARY KEY,
  data_sources_id UUID NOT NULL REFERENCES data_sources(id),
  product_url TEXT NOT NULL UNIQUE,
  moved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  attempt_logs JSONB NOT NULL
);

CREATE TABLE product_queue_archive (
  id BIGSERIAL PRIMARY KEY,
  data_sources_id UUID NOT NULL REFERENCES data_sources(id),
  product_url TEXT NOT NULL UNIQUE,
  archived_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
