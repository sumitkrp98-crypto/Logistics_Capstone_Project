-- ==========================
-- Carrier Master Data
-- ==========================

INSERT INTO logistics.dim_carrier
(carrier_id, carrier_name, service_tier, valid_from, is_current)
VALUES
('C001','DHL','Premium','2026-07-01',TRUE),
('C002','FedEx','Premium','2026-07-01',TRUE),
('C003','Blue Dart','Standard','2026-07-01',TRUE),
('C004','Delhivery','Economy','2026-07-01',TRUE),
('C005','Ecom Express','Economy','2026-07-01',TRUE);

-- ==========================
-- Warehouse Master Data
-- ==========================

INSERT INTO logistics.dim_warehouse
(warehouse_id, warehouse_name, region, valid_from, is_current)
VALUES
('W001','Delhi_WH01','North','2026-07-01',TRUE),
('W002','Mumbai_WH02','West','2026-07-01',TRUE),
('W003','Bengaluru_WH03','South','2026-07-01',TRUE),
('W004','Hyderabad_WH04','South','2026-07-01',TRUE),
('W005','Chennai_WH05','South','2026-07-01',TRUE);

-- ==========================
-- Currency Master
-- ==========================

INSERT INTO logistics.dim_currency
(currency_code,currency_name)
VALUES
('INR','Indian Rupee'),
('USD','US Dollar');
-- Date Dimension
INSERT INTO logistics.dim_date
(date_key, year, month, day, month_name, day_of_week, is_weekend)
SELECT
    d::date,
    EXTRACT(YEAR FROM d),
    EXTRACT(MONTH FROM d),
    EXTRACT(DAY FROM d),
    TO_CHAR(d,'Month'),
    TO_CHAR(d,'Day'),
    CASE
        WHEN EXTRACT(ISODOW FROM d) IN (6,7)
        THEN TRUE
        ELSE FALSE
    END
FROM generate_series(
    '2026-07-01'::date,
    '2026-07-31'::date,
    interval '1 day'
) d
ON CONFLICT (date_key) DO NOTHING;