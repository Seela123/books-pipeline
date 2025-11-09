{{ config(materialized='table') }}

with base as (

    select

        md5(trim(product_url)) as record_id,
        trim(title) as title,


        coalesce(
            price::numeric,
            cast(
                nullif(
                    regexp_replace(coalesce(price_raw, ''), '[^0-9\.]', '', 'g'),
                    ''
                ) as numeric(10,2)
            )
        ) as price,


        coalesce(
            rating,
            case rating_raw
                when 'One'   then 1
                when 'Two'   then 2
                when 'Three' then 3
                when 'Four'  then 4
                when 'Five'  then 5
            end
        )::int as rating,

        coalesce(in_stock, false) as in_stock,
        trim(product_url) as product_url,


        now()::timestamptz as load_ts

    from {{ source('bronze', 'books_toscrape') }}

),

dedup as (
    select
        *,
        row_number() over (
            partition by record_id
            order by load_ts desc nulls last
        ) as rn
    from base
)

select
    record_id,
    title,
    price,
    rating,
    in_stock,
    product_url,
    load_ts
from dedup
where rn = 1
