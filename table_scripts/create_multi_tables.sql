-- Create admin2 table
DROP TABLE IF EXISTS public.admin2;
CREATE TABLE public.admin2 (
    id SERIAL PRIMARY KEY,
    admin2_code VARCHAR(255) NOT NULL
);

-- Populate the "admin2" table with unique admin2_code valeus
INSERT INTO public.admin2 (admin2_code)
SELECT DISTINCT ON (admin2_code) admin2_code
FROM public.themes
WHERE admin2_code IS NOT NULL;

-- Update the "public.themes" table with foreign keys
ALTER TABLE public.themes
ADD COLUMN admin2_id INTEGER;
UPDATE public.themes AS t
SET admin2_id = a.id
FROM public.admin2 AS a
WHERE t.admin2_code = a.admin2_code;

-- Create the "themes_multi" table
DROP TABLE IF EXISTS public.themes_multi;
CREATE TABLE public.themes_multi (
    id SERIAL PRIMARY KEY,
    admin0_code_iso3 VARCHAR(255) NOT NULL,
    admin1_code VARCHAR(255),
    admin2_id INTEGER REFERENCES public.admin2 (id),
    start_date DATE,
    end_date DATE,
    datum_id INTEGER NOT NULL,
    theme VARCHAR(255) NOT NULL,
    key VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL
);

-- Copy data from themes to themes_multi
INSERT INTO public.themes_multi (
    admin0_code_iso3,
    admin1_code,
    admin2_id,
    start_date,
    end_date,
    datum_id,
    theme,
    key,
    value
)
SELECT
    admin0_code_iso3,
    admin1_code,
    admin2_id,
    start_date,
    end_date,
    datum_id,
    theme,
    key,
    value
FROM public.themes;

-- Drop the extra column admin2_id from themes
ALTER TABLE public.themes
DROP COLUMN IF EXISTS admin2_id;
