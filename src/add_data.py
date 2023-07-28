import logging
import string
from datetime import date, timedelta
from itertools import product

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from src import settings, utils

logger = logging.getLogger(__name__)


# Settings for generating the fake data
_N_ISO3 = 23
_N_ADMIN2 = 500
_N_THEMES = 10
_ADMIN1_CODE = "P001"  # just use the same admin1 everywhere

# Create some handy lists
_RNG = np.random.default_rng(12345)
_ISO3S = [
    "".join(_RNG.choice(list(string.ascii_uppercase), 3))
    for _ in range(_N_ISO3)
]
_DATES = [date(2000, 1, 1) + timedelta(days=i) for i in range(9_000)]

# Settings for memory management
_DB_INSERTION_CHUNK_SIZE = 100_000
_FAKE_DATA_DIMENSION_SIZE = 5


def add_afg_pop_data(datum_id_min: int = 0) -> int:
    logger.info("Adding AFG population data")
    df = _get_afg_pop_data(datum_id_min=datum_id_min)
    _add_df_to_table(df)
    return df.loc[:, "datum_id"].max()


def add_fake_pop_data(datum_id_min: int = 0) -> int:
    logger.info("Generating synthetic population data")
    df = _generate_fake_pop_data(datum_id_min)
    logger.info("Adding synthetic population data to table")
    _add_df_to_table(df)
    return df.loc[:, "datum_id"].max()


def add_fake_data(datum_id_min: int = 0) -> int:
    logger.info("Generating synthetic general data")
    df = _generate_fake_data(datum_id_min)
    logger.info("Adding synthetic data to the table")
    _add_df_to_table(df)
    return df.loc[:, "datum_id"].max()


def _add_df_to_table(df: pd.DataFrame):
    engine = create_engine(utils.get_connection_string())
    df.to_sql(
        name=settings.table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=_DB_INSERTION_CHUNK_SIZE,
    )


def _get_afg_pop_data(datum_id_min: int = 0) -> pd.DataFrame:
    # Read in the data and clean
    dataset_url = "https://data.humdata.org/dataset/17acb541-9431-409a-80a8-50eda7e8ebab/resource/dc7a5656-d557-404f-8b1d-494c7bbd0112/download/afg_admpop_adm1_2021_v2.csv"
    df = (
        pd.read_csv(dataset_url, skiprows=[1])
        .rename(columns=lambda x: x.strip())
        .rename(
            columns={
                "Admin1_Code": "admin1_code",
            }
        )
        .drop(columns=["Admin0_Name", "Admin0_Code", "Admin1_Name"])
    )
    df["admin0_code_iso3"] = "AFG"
    df["theme"] = "population"

    # Melt the dataframe
    id_vars = ["admin0_code_iso3", "admin1_code", "theme"]
    df_melted = df.melt(
        id_vars=id_vars, var_name="key", value_name="population"
    )

    # Extract 'sex' and 'age' from the 'key' column
    df_melted[["sex", "age"]] = df_melted["key"].str.split(
        "_", n=1, expand=True
    )[[0, 1]]
    # drop key
    df_melted = df_melted.drop(columns=["key"])

    # Create a unique identifier
    df_melted["datum_id"] = np.arange(
        datum_id_min, len(df_melted) + datum_id_min
    )

    # Split into separate rows for each ID
    df_combined = pd.DataFrame()
    for cname in ["sex", "age", "population"]:
        df_melted_cname = df_melted[id_vars + ["datum_id", cname]].rename(
            columns={cname: "value"}
        )
        df_melted_cname["key"] = cname
        df_combined = pd.concat([df_combined, df_melted_cname])

    # Add missing params
    df_combined["start_date"] = date(2023, 1, 1)
    df_combined["admin1_code"] = _ADMIN1_CODE

    return df_combined


def _generate_fake_pop_data(datum_id_min: int = 0) -> pd.DataFrame:
    # Assume 500 admin regions per country
    admin2_codes = ["P{:04d}".format(i) for i in range(500)]
    ages = list(range(20))  # 20 different ages
    sexes = ["F", "M"]

    # Generate all combinations of _ISO3S, admin2_codes, ages, and sexes
    combinations = list(product(_ISO3S, admin2_codes, ages, sexes))

    # Separate the combinations into individual arrays for each column
    # They each need to repeat three times for the dimesions
    nrows_per_datum = 3
    iso3_arr = np.array(
        [[comb[0]] * nrows_per_datum for comb in combinations]
    ).ravel()
    admin2_code_arr = np.array(
        [[comb[1]] * nrows_per_datum for comb in combinations]
    ).ravel()
    # Generate a datum ID for each datum
    datum_id_arr = np.repeat(
        np.arange(len(combinations)) + datum_id_min, nrows_per_datum
    )

    # Then these will alternate
    age_arr = np.array([f"{comb[2]:02d}" for comb in combinations])
    sex_arr = np.array([comb[3] for comb in combinations])
    population_arr = np.random.randint(10000, 200001, size=len(combinations))

    key_arr = ["age", "sex", "population"] * len(combinations)
    values_arr = np.column_stack([age_arr, sex_arr, population_arr]).ravel()

    # Combine all arrays into the DataFrame with the updated column names
    df = pd.DataFrame(
        {
            "theme": "population",
            "admin0_code_iso3": iso3_arr,
            "admin1_code": _ADMIN1_CODE,
            "admin2_code": admin2_code_arr,
            "start_date": date(2023, 1, 1),
            "datum_id": datum_id_arr,
            "key": key_arr,
            "value": values_arr,
        }
    )

    return df


def _generate_fake_data(
    datum_id_min: int = 0, dimension_size: int = _FAKE_DATA_DIMENSION_SIZE
) -> pd.DataFrame:
    """
    Generate a fake dataset with two dimensions, one indicator, and
    randomly generated ISO3s, pcodes, and data.
    The main parameter for controlling the size is the dimension size, which
    sets how many options each of the three dimensions has.
    The dataset has 23 ISO3s, 500 admin 2 regions, two dimensions and
    one indicator. This means the size (in rows) will be
    23 x 500 x 3 x dimension_size. Should be set to the max that your
    memory can handle.
    """
    logger.info(
        f"Generating dataset with {23 * 500 * 3 * dimension_size} rows."
    )
    # Assume 10 themes and 500 admin2 codes
    themes = ["theme{:02d}".format(i) for i in range(_N_THEMES)]
    admin2_codes = ["P{:04d}".format(i) for i in range(_N_ADMIN2)]
    dim1 = ["dim1_{:03d}".format(i) for i in range(dimension_size)]
    dim2 = ["dim2_{:03d}".format(i) for i in range(dimension_size)]

    # Generate all combinations
    combinations = list(product(themes, _ISO3S, admin2_codes, dim1, dim2))

    # Separate the combinations into individual arrays for each column
    # They each need to repeat three times since there are two dimensions
    # and one indicator
    nrows_per_datum = 3
    theme_arr = np.array(
        [[comb[0]] * nrows_per_datum for comb in combinations]
    ).ravel()
    iso3_arr = np.array(
        [[comb[1]] * nrows_per_datum for comb in combinations]
    ).ravel()
    admin2_code_arr = np.array(
        [[comb[2]] * nrows_per_datum for comb in combinations]
    ).ravel()
    # Generate a datum ID for each datum
    datum_id_arr = np.repeat(
        np.arange(len(combinations)) + datum_id_min, nrows_per_datum
    )

    # Then these will alternate
    dim1_arr = np.array([comb[3] for comb in combinations])
    dim2_arr = np.array([comb[4] for comb in combinations])
    indicator_arr = np.random.randint(10000, 200001, size=len(combinations))

    key_arr = ["dim1", "dim2", "indicator"] * len(combinations)
    values_arr = np.column_stack([dim1_arr, dim2_arr, indicator_arr]).ravel()

    dates_arr = _RNG.choice(_DATES, len(key_arr))

    # Combine all arrays into the DataFrame with the updated column names
    df = pd.DataFrame(
        {
            "theme": theme_arr,
            "admin0_code_iso3": iso3_arr,
            "admin1_code": _ADMIN1_CODE,
            "admin2_code": admin2_code_arr,
            "start_date": dates_arr,
            "end_date": dates_arr,
            "datum_id": datum_id_arr,
            "key": key_arr,
            "value": values_arr,
        }
    )

    return df
