SELECT gender, ROUND(AVG(age), 1) AS avg_age
FROM consumers
GROUP BY gender
ORDER BY gender;
