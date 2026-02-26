WITH high_value AS (
    SELECT
        consumer_id,
        SUM(item_total) AS spend_nov_dec,
        COUNT(DISTINCT order_id) AS orders_nov_dec
    FROM itemized_orders
    WHERE order_status = 'delivered'
      AND order_timestamp >= '2025-11-01'
      AND order_timestamp < '2026-01-01'
    GROUP BY consumer_id
    HAVING SUM(item_total) >= 5000
),
feb_activity AS (
    SELECT DISTINCT consumer_id
    FROM itemized_orders
    WHERE order_timestamp >= '2026-02-01'
      AND order_timestamp < '2026-03-01'
)
SELECT
    h.consumer_id,
    c.gender,
    c.age,
    s.store_name AS nearest_store,
    h.spend_nov_dec,
    h.orders_nov_dec,
    MAX(io.order_timestamp) AS last_order_date
FROM high_value h
LEFT JOIN feb_activity f ON h.consumer_id = f.consumer_id
JOIN consumers c ON h.consumer_id = c.consumer_id
JOIN stores s ON c.nearest_store_id = s.store_id
JOIN itemized_orders io ON h.consumer_id = io.consumer_id AND io.order_status = 'delivered'
WHERE f.consumer_id IS NULL
GROUP BY h.consumer_id, c.gender, c.age, s.store_name, h.spend_nov_dec, h.orders_nov_dec
ORDER BY h.spend_nov_dec DESC;
