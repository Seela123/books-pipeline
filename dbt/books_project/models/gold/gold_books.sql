{{ config(
    materialized = 'table',
    schema = 'gold'
) }}

SELECT
    rating,
    ROUND(AVG(price), 2) AS avg_price_rating,
    MAX(price) AS max_price_on_rating,
    MIN(price) AS min_price_on_rating,
    COUNT(*) AS total_books_rating
FROM {{ ref('silver_books') }}
GROUP BY rating
ORDER BY rating DESC
