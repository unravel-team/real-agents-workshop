
SELECT pc.brand_name, SUM(io.item_total) AS total_revenue
FROM itemized_orders io
JOIN product_catalogue pc ON io.product_id = pc.product_id
WHERE pc.category = 'Snacks & Munchies'
  AND io.order_status = 'delivered'
GROUP BY pc.brand_name
ORDER BY total_revenue DESC
LIMIT 3;
