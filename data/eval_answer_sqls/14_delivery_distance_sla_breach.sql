SELECT
    s.store_name,
    CASE
        WHEN distance_km <= 1 THEN '0-1 km'
        WHEN distance_km <= 2 THEN '1-2 km'
        WHEN distance_km <= 3 THEN '2-3 km'
        WHEN distance_km <= 4 THEN '3-4 km'
        ELSE '4+ km'
    END AS distance_bucket,
    COUNT(DISTINCT order_id) AS delivered_orders,
    ROUND(AVG(actual_delivery_secs) / 60.0, 1) AS avg_delivery_mins,
    ROUND(AVG(committed_delivery_secs) / 60.0, 1) AS avg_committed_mins,
    ROUND(AVG(actual_delivery_secs - committed_delivery_secs) / 60.0, 1) AS avg_delay_mins,
    ROUND(COUNT(DISTINCT order_id) FILTER (
        WHERE actual_delivery_secs > committed_delivery_secs
    ) * 100.0 / COUNT(DISTINCT order_id), 2) AS sla_breach_pct
FROM itemized_orders
JOIN stores s USING (store_id)
WHERE order_status = 'delivered'
GROUP BY s.store_name, distance_bucket
ORDER BY s.store_name, distance_bucket;
