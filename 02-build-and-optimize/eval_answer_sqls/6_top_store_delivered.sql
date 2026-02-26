SELECT s.store_name, COUNT(DISTINCT io.order_id) AS delivered_orders
FROM itemized_orders io
JOIN stores s ON io.store_id = s.store_id
WHERE io.order_status = 'delivered'
GROUP BY s.store_name
ORDER BY delivered_orders DESC
LIMIT 1;
