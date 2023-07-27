import logging

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from src import settings, utils

logger = logging.getLogger(__name__)


def add_afg_pop_data():
    logger.info("Adding population data")
    engine = create_engine(utils.get_connection_string())
    df = _get_afg_pop_data()
    df.to_sql(
        name=settings.table_name, con=engine, if_exists="append", index=False
    )


def _get_afg_pop_data():
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
    df_melted["record_id"] = np.arange(len(df_melted))

    # Split into separate rows for each ID
    df_combined = pd.DataFrame()
    for cname in ["sex", "age", "population"]:
        df_melted_cname = df_melted[id_vars + ["record_id", cname]].rename(
            columns={cname: "value"}
        )
        df_melted_cname["key"] = cname
        df_combined = pd.concat([df_combined, df_melted_cname])

    return df_combined
