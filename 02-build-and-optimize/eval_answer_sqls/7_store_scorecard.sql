WITH order_agg AS (
    SELECT
        store_id,
        STRFTIME(order_timestamp, '%Y-%m') AS month,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT order_id) FILTER (WHERE order_status = 'delivered') AS delivered_orders,
        COUNT(DISTINCT order_id) FILTER (WHERE order_status = 'cancelled') AS cancelled_orders,
        SUM(item_total) FILTER (WHERE order_status = 'delivered') AS gross_revenue,
        SUM(discount * quantity) FILTER (WHERE order_status = 'delivered') AS total_discount_given,
        AVG(actual_delivery_secs) FILTER (WHERE order_status = 'delivered') AS avg_delivery_secs,
        COUNT(DISTINCT order_id) FILTER (
            WHERE order_status = 'delivered' AND actual_delivery_secs > committed_delivery_secs
        ) AS sla_breached_orders
    FROM itemized_orders
    GROUP BY store_id, STRFTIME(order_timestamp, '%Y-%m')
)
SELECT
    s.store_name,
    s.area,
    o.month,
    o.total_orders,
    o.delivered_orders,
    ROUND(o.cancelled_orders * 100.0 / NULLIF(o.total_orders, 0), 2) AS cancellation_rate_pct,
    ROUND(o.gross_revenue, 0) AS gross_revenue,
    ROUND(o.total_discount_given, 0) AS discount_given,
    ROUND(o.gross_revenue - o.total_discount_given, 0) AS net_revenue,
    ROUND(o.avg_delivery_secs / 60.0, 1) AS avg_delivery_mins,
    ROUND(o.sla_breached_orders * 100.0 / NULLIF(o.delivered_orders, 0), 2) AS sla_breach_pct
FROM order_agg o
JOIN stores s USING (store_id)
ORDER BY s.store_name, o.month;
