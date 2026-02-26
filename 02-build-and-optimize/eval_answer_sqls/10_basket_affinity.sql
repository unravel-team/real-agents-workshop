WITH order_subcats AS (
    SELECT DISTINCT
        o.order_id,
        p.sub_category
    FROM itemized_orders o
    JOIN product_catalogue p USING (product_id)
    WHERE o.order_status = 'delivered'
)
SELECT
    a.sub_category AS subcat_a,
    b.sub_category AS subcat_b,
    COUNT(*) AS co_occurrence_count,
    ROUND(COUNT(*) * 100.0 / (
        SELECT COUNT(DISTINCT order_id) FROM itemized_orders WHERE order_status = 'delivered'
    ), 2) AS pct_of_all_orders
FROM order_subcats a
JOIN order_subcats b
    ON a.order_id = b.order_id
    AND a.sub_category < b.sub_category
GROUP BY a.sub_category, b.sub_category
ORDER BY co_occurrence_count DESC
LIMIT 25;
