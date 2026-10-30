CREATE TABLE sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL
);

CREATE TABLE raw_ingestions (
  id BIGSERIAL PRIMARY KEY,
  sources_id UUID REFERENCES sources(id),
  scraped_at TIMESTAMPTZ DEFAULT now(),
  img_url TEXT,
  payload JSONB NOT NULL,
  proccessed_at TIMESTAMPTZ
);

ALTER TABLE sources RENAME TO data_sources;

ALTER TABLE raw_ingestions RENAME COLUMN sources_id TO data_sources_id;
ALTER TABLE raw_ingestions RENAME COLUMN scraped_at TO ingested_at;
ALTER TABLE raw_ingestions DROP COLUMN proccessed_at;
ALTER TABLE raw_ingestions ADD COLUMN ingested_by text;

CREATE TYPE product_queue_status AS ENUM ('waiting', 'in_progress', 'paused');

CREATE TABLE product_queue (
  id BIGSERIAL PRIMARY KEY,
  data_sources_id UUID NOT NULL REFERENCES data_sources(id),
  last_raw_ingestions_id BIGSERIAL NOT NULL REFERENCES raw_ingestions(id),
  product_url TEXT NOT NULL UNIQUE,
  next_ingestion_due TIMESTAMPTZ NOT NULL DEFAULT now(),
  status product_queue_status NOT NULL DEFAULT 'waiting',
  claimed_at TIMESTAMPTZ,
  claimed_by TEXT,
  attempt_count SMALLINT NOT NULL DEFAULT 0,
  attempt_logs JSONB DEFAULT '[]'::jsonb
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