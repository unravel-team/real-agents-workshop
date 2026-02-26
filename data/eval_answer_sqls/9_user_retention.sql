WITH first_order AS (
    SELECT
        consumer_id,
        DATE_TRUNC('month', MIN(order_timestamp))::DATE AS cohort_month
    FROM itemized_orders
    WHERE order_status = 'delivered'
    GROUP BY consumer_id
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM first_order
    GROUP BY cohort_month
),
monthly_activity AS (
    SELECT DISTINCT
        consumer_id,
        DATE_TRUNC('month', order_timestamp)::DATE AS active_month
    FROM itemized_orders
    WHERE order_status = 'delivered'
),
retention AS (
    SELECT
        f.cohort_month,
        DATEDIFF('month', f.cohort_month, m.active_month) AS months_since_first,
        COUNT(DISTINCT f.consumer_id) AS retained_consumers
    FROM first_order f
    JOIN monthly_activity m
        ON f.consumer_id = m.consumer_id
        AND m.active_month >= f.cohort_month
    GROUP BY f.cohort_month, DATEDIFF('month', f.cohort_month, m.active_month)
)
SELECT
    r.cohort_month,
    cs.cohort_size,
    ROUND(MAX(CASE WHEN months_since_first = 0 THEN retained_consumers END) * 100.0 / cs.cohort_size, 1) AS "M0 %",
    ROUND(MAX(CASE WHEN months_since_first = 1 THEN retained_consumers END) * 100.0 / cs.cohort_size, 1) AS "M1 %",
    ROUND(MAX(CASE WHEN months_since_first = 2 THEN retained_consumers END) * 100.0 / cs.cohort_size, 1) AS "M2 %",
    ROUND(MAX(CASE WHEN months_since_first = 3 THEN retained_consumers END) * 100.0 / cs.cohort_size, 1) AS "M3 %"
FROM retention r
JOIN cohort_sizes cs ON r.cohort_month = cs.cohort_month
GROUP BY r.cohort_month, cs.cohort_size
ORDER BY r.cohort_month;
