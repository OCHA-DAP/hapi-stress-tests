EXPLAIN ANALYZE
SELECT
    tm.*,
    a.admin2_code AS admin2_code
FROM
    public.themes_multi AS tm
JOIN
    public.admin2 AS a ON tm.admin2_id = a.id
WHERE
    tm.theme = 'theme00' AND tm.admin0_code_iso3 = 'BXM';
