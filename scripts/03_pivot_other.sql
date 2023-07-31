EXPLAIN ANALYZE
SELECT
    id,
    admin0_code_iso3,
    admin1_code,
    admin2_code,
    start_date,
    end_date,
    datum_id,
    theme,
    MAX(CASE WHEN key = 'dim1' THEN value END) AS dim1,
    MAX(CASE WHEN key = 'dim2' THEN value END) AS dim2,
    MAX(CASE WHEN key = 'indicator' THEN value END) AS indicator
FROM public.themes
WHERE theme = 'theme01' AND admin0_code_iso3 = 'BXM'
GROUP BY
    id,
    admin0_code_iso3,
    admin1_code,
    admin2_code,
    start_date,
    end_date,
    datum_id,
    theme;
