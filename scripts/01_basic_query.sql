EXPLAIN ANALYZE
SELECT *
FROM public.themes
WHERE theme = 'theme00'
  AND admin0_code_iso3 = 'BXM'
  AND start_date > '2020-01-01';
