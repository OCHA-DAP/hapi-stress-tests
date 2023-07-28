import logging
import string
from itertools import product

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from src import settings, utils

logger = logging.getLogger(__name__)
_RNG = np.random.default_rng(12345)
_ISO3S = [
    "".join(_RNG.choice(list(string.ascii_uppercase), 3)) for _ in range(23)
]


def add_afg_pop_data(datum_id_min: int = 0) -> int:
    logger.info("Adding AFG population data")
    df = _get_afg_pop_data(datum_id_min=datum_id_min)
    _add_df_to_table(df)
    return df.loc[:, "datum_id"].max()


def add_fake_pop_data(datum_id_min: int = 0):
    logger.info("Generating synthetic population data")
    df = _generate_fake_pop_data(datum_id_min)
    logger.info("Adding synthetic population data to table")
    _add_df_to_table(df)
    return df.loc[:, "datum_id"].max()


def _add_df_to_table(df: pd.DataFrame):
    engine = create_engine(utils.get_connection_string())
    df.to_sql(
        name=settings.table_name, con=engine, if_exists="append", index=False
    )


def _get_afg_pop_data(datum_id_min: int = 0):
    # Read in the data and clean
    dataset_url = "https://data.humdata.org/dataset/17acb541-9431-409a-80a8-50eda7e8ebab/resource/dc7a5656-d557-404f-8b1d-494c7bbd0112/download/afg_admpop_adm1_2021_v2.csv"
    df = (
        pd.read_csv(dataset_url, skiprows=[1])
        .rename(columns=lambda x: x.strip())
        .rename(
            columns={
                "Admin1_Name": "admin1_name",
                "Admin1_Code": "admin1_code",
            }
        )
        .drop(columns=["Admin0_Name", "Admin0_Code"])
    )
    df["admin0_code_iso3"] = "AFG"
    df["theme_name"] = "population"

    # Melt the dataframe
    id_vars = ["admin0_code_iso3", "admin1_name", "admin1_code", "theme_name"]
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

    return df_combined


def _generate_fake_pop_data(datum_id_min: int = 0):
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
            "admin0_code_iso3": iso3_arr,
            "admin2_code": admin2_code_arr,
            "datum_id": datum_id_arr,
            "key": key_arr,
            "value": values_arr,
        }
    )

    return df
