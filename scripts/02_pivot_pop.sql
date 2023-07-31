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
    MAX(CASE WHEN key = 'sex' THEN value END) AS sex,
    MAX(CASE WHEN key = 'age' THEN value END) AS age,
    MAX(CASE WHEN key = 'population' THEN value END) AS population
FROM public.themes
WHERE theme = 'population' AND admin0_code_iso3 = 'AFG'
GROUP BY
    id,
    admin0_code_iso3,
    admin1_code,
    admin2_code,
    start_date,
    end_date,
    datum_id,
    theme;
