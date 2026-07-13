CREATE TABLE time_series (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    value FLOAT NOT NULL,
    metadata JSONB
);

CREATE INDEX idx_time_series_timestamp ON time_series (timestamp);