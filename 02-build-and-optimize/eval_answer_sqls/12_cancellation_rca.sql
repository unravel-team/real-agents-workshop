WITH cancel_data AS (
    SELECT
        store_id,
        cancel_reason,
        EXTRACT(HOUR FROM order_timestamp) AS hour_of_day,
        order_id
    FROM itemized_orders
    WHERE order_status = 'cancelled'
)
SELECT
    s.store_name,
    cd.cancel_reason,
    CASE
        WHEN cd.hour_of_day BETWEEN 6 AND 11 THEN 'Morning (6-12)'
        WHEN cd.hour_of_day BETWEEN 12 AND 16 THEN 'Afternoon (12-5)'
        WHEN cd.hour_of_day BETWEEN 17 AND 21 THEN 'Evening (5-10)'
        ELSE 'Night (10-6)'
    END AS time_slot,
    COUNT(DISTINCT cd.order_id) AS cancelled_orders,
    ROUND(COUNT(DISTINCT cd.order_id) * 100.0 / SUM(COUNT(DISTINCT cd.order_id)) OVER (PARTITION BY s.store_name), 2) AS pct_of_store_cancellations
FROM cancel_data cd
JOIN stores s USING (store_id)
GROUP BY s.store_name, cd.cancel_reason, time_slot
ORDER BY s.store_name, cancelled_orders DESC;
