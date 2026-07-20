-- 1. Shipment volume and freight cost by warehouse and month in USD
SELECT 
    w.warehouse_name,
    DATE_TRUNC('month', f.date_key) AS month,
    COUNT(f.shipment_id) AS total_shipments,
    SUM(f.freight_cost_usd) AS total_freight_cost_usd
FROM logistics.fact_shipment f
JOIN logistics.dim_warehouse w ON f.warehouse_key = w.warehouse_key
GROUP BY w.warehouse_name, DATE_TRUNC('month', f.date_key)
ORDER BY month, total_shipments DESC;

-- 2. Top carriers by volume
SELECT 
    c.carrier_name,
    COUNT(f.shipment_id) AS total_shipments,
    SUM(f.freight_cost_usd) AS total_freight_cost_usd
FROM logistics.fact_shipment f
JOIN logistics.dim_carrier c ON f.carrier_key = c.carrier_key
GROUP BY c.carrier_name
ORDER BY total_shipments DESC;

-- 3. Exception rate by warehouse
SELECT 
    w.warehouse_name,
    COUNT(f.shipment_id) AS total_shipments,
    SUM(CASE WHEN f.exception_flag = TRUE THEN 1 ELSE 0 END) AS exception_count,
    ROUND(
        (SUM(CASE WHEN f.exception_flag = TRUE THEN 1 ELSE 0 END)::NUMERIC / COUNT(f.shipment_id)) * 100, 
        2
    ) AS exception_rate_percentage
FROM logistics.fact_shipment f
JOIN logistics.dim_warehouse w ON f.warehouse_key = w.warehouse_key
GROUP BY w.warehouse_name;

-- 4. Month-over-Month Growth (using CTE and Window Function)
WITH monthly_summary AS (
    SELECT 
        DATE_TRUNC('month', date_key) AS shipment_month,
        COUNT(shipment_id) AS current_month_volume,
        SUM(freight_cost_usd) AS current_month_cost
    FROM logistics.fact_shipment
    GROUP BY DATE_TRUNC('month', date_key)
)
SELECT 
    shipment_month,
    current_month_volume,
    LAG(current_month_volume) OVER (ORDER BY shipment_month) AS previous_month_volume,
    ROUND(
        ((current_month_volume - LAG(current_month_volume) OVER (ORDER BY shipment_month))::NUMERIC / 
        NULLIF(LAG(current_month_volume) OVER (ORDER BY shipment_month), 0)) * 100, 
        2
    ) AS volume_growth_percentage
FROM monthly_summary;

-- 5. Custom Query: Data Quality Issue Breakdown per File
SELECT 
    source_file,
    rows_read,
    rows_loaded,
    rows_quarantined,
    rows_rejected,
    rows_autocorrected,
    run_timestamp
FROM logistics.dq_run_summary
ORDER BY run_timestamp DESC;

