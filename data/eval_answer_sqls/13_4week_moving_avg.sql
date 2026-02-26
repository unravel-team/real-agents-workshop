WITH weekly AS (
    SELECT
        store_id,
        DATE_TRUNC('week', order_timestamp)::DATE AS week_start,
        SUM(item_total) FILTER (WHERE order_status = 'delivered') AS revenue,
        COUNT(DISTINCT order_id) FILTER (WHERE order_status = 'delivered') AS orders,
        COUNT(DISTINCT consumer_id) AS unique_consumers
    FROM itemized_orders
    GROUP BY store_id, DATE_TRUNC('week', order_timestamp)
)
SELECT
    s.store_name,
    w.week_start,
    w.revenue,
    w.orders,
    w.unique_consumers,
    ROUND(AVG(w.revenue) OVER (
        PARTITION BY w.store_id ORDER BY w.week_start
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 0) AS revenue_4wk_ma,
    ROUND((w.revenue - LAG(w.revenue) OVER (PARTITION BY w.store_id ORDER BY w.week_start))
        * 100.0 / NULLIF(LAG(w.revenue) OVER (PARTITION BY w.store_id ORDER BY w.week_start), 0)
    , 2) AS wow_growth_pct
FROM weekly w
JOIN stores s USING (store_id)
ORDER BY s.store_name, w.week_start;
