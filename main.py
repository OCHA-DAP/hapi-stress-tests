import argparse
import logging

import coloredlogs

from src import add_data, setup

coloredlogs.install(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recreate-db", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    datum_id_max = 0
    args = get_args()
    setup.create_db(recreate_db=args.recreate_db)
    setup.create_table()
    datum_id_max = add_data.add_afg_pop_data()
    datum_id_max = add_data.add_fake_pop_data(datum_id_min=datum_id_max + 1)
    # Add the rest of the data in batches for memory reasons
    nbatches = 1  # this will give aobut 25 mil rows
    logger.info(f"Adding {nbatches} batches ")
    for i in range(nbatches):
        logger.info(f"On batch number {i}")
        datum_id_max = add_data.add_fake_data(datum_id_min=datum_id_max + 1)
