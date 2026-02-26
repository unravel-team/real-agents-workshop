SELECT
    s.store_name,
    DAYNAME(o.order_timestamp) AS day_of_week,
    EXTRACT(DOW FROM o.order_timestamp) AS dow_num,
    EXTRACT(HOUR FROM o.order_timestamp) AS hour_of_day,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(SUM(o.item_total), 0) AS revenue,
    ROUND(AVG(o.actual_delivery_secs) FILTER (WHERE o.order_status = 'delivered') / 60.0, 1) AS avg_delivery_mins
FROM itemized_orders o
JOIN stores s USING (store_id)
GROUP BY s.store_name, DAYNAME(o.order_timestamp), EXTRACT(DOW FROM o.order_timestamp), EXTRACT(HOUR FROM o.order_timestamp)
ORDER BY s.store_name, dow_num, hour_of_day;
