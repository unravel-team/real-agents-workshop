SELECT order_status, COUNT(DISTINCT order_id) AS order_count
FROM itemized_orders
GROUP BY order_status
ORDER BY order_count DESC;
