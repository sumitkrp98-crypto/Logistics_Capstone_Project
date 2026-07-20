CREATE SCHEMA IF NOT EXISTS logistics;

-- Dimension tables
CREATE TABLE IF NOT EXISTS logistics.dim_carrier (
    carrier_key     SERIAL PRIMARY KEY,
    carrier_id      VARCHAR(20) NOT NULL,
    carrier_name    VARCHAR(200) NOT NULL,
    service_tier    VARCHAR(20) NOT NULL,
    valid_from      DATE NOT NULL,
    valid_to        DATE,
    is_current      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS logistics.dim_warehouse (
    warehouse_key   SERIAL PRIMARY KEY,
    warehouse_id    VARCHAR(20) NOT NULL,
    warehouse_name  VARCHAR(200) NOT NULL,
    region          VARCHAR(50) NOT NULL,
    valid_from      DATE NOT NULL,
    valid_to        DATE,
    is_current      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS logistics.dim_date (
    date_key        DATE PRIMARY KEY,
    year            INT NOT NULL,
    month           INT NOT NULL,
    day             INT NOT NULL,
    month_name      VARCHAR(20) NOT NULL,
    day_of_week     VARCHAR(20) NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS logistics.dim_currency (
    currency_code   VARCHAR(3) PRIMARY KEY,
    currency_name   VARCHAR(50)
);

-- Fact table
CREATE TABLE IF NOT EXISTS logistics.fact_shipment (
    shipment_id         VARCHAR(30) PRIMARY KEY,
    warehouse_key       INT REFERENCES logistics.dim_warehouse(warehouse_key),
    carrier_key         INT REFERENCES logistics.dim_carrier(carrier_key),
    date_key            DATE REFERENCES logistics.dim_date(date_key),
    customer_id         VARCHAR(20),
    destination_code    VARCHAR(20),
    service_level       VARCHAR(20),
    weight_kg           NUMERIC(10,2),
    freight_cost_local  NUMERIC(12,2),
    currency_code       VARCHAR(3),
    freight_cost_usd    NUMERIC(12,2),
    exception_flag      BOOLEAN NOT NULL DEFAULT FALSE,
    ship_timestamp      TIMESTAMP,
    source_file         VARCHAR(200),
    load_batch_id       VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_fact_shipment_date ON logistics.fact_shipment(date_key);

-- Data quality tables
CREATE TABLE IF NOT EXISTS logistics.shipment_quarantine (
    shipment_id     VARCHAR(30),
    reason          VARCHAR(200),
    raw_row         JSONB,
    source_file     VARCHAR(200),
    quarantined_at  TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS logistics.dq_run_summary (
    run_id              SERIAL PRIMARY KEY,
    source_file         VARCHAR(200),
    run_timestamp       TIMESTAMP DEFAULT now(),
    rows_read           INT,
    rows_loaded         INT,
    rows_quarantined    INT,
    rows_rejected       INT,
    rows_autocorrected  INT
);

-- Idempotency tracker (yeh table batayegi konsi file already load ho chuki hai)
CREATE TABLE IF NOT EXISTS logistics.processed_files (
    file_name       VARCHAR(200) PRIMARY KEY,
    processed_at    TIMESTAMP DEFAULT now(),
    row_count       INT
);

-- Insert baseline carrier data with history tracking (SCD Type 2)
INSERT INTO logistics.dim_carrier 
(carrier_id, carrier_name, service_tier, valid_from, valid_to, is_current)
VALUES 
('DHL', 'DHL', 'Standard', '2026-07-01', '2026-07-10', FALSE),
('DHL', 'DHL', 'Express', '2026-07-11', NULL, TRUE),
('FedEx', 'FedEx', 'Standard', '2026-07-01', NULL, TRUE),
('Blue Dart', 'Blue Dart', 'Express', '2026-07-01', NULL, TRUE),
('Delhivery', 'Delhivery', 'Standard', '2026-07-01', NULL, TRUE),
('Ecom Express', 'Ecom Express', 'Standard', '2026-07-01', NULL, TRUE);