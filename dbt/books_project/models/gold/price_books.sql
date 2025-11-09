{{config (
        materialized = 'table',
        schema = 'gold' )}}



WITH category AS (
SELECT
COUNT(*) as total_books,
 CASE
	WHEN price < 10 THEN '0-10'
	WHEN price >=10 AND price <= 20 THEN '10-20'
	WHEN price >=20 AND price <= 30 THEN '20-30'
	WHEN price >=30 AND price <= 40	THEN '30-40'
	WHEN price >=40 AND price <= 50 THEN '40-50'
	WHEN price >=50 AND price <= 60 THEN '50-60'
	END AS price_range
	FROM {{ ref('silver_books') }}
	GROUP BY price_range
)
SELECT price_range,total_books
FROM category
ORDER BY price_range DESC
