import argparse
import logging

from src import add_data, setup

logging.basicConfig(level=logging.INFO)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recreate-db", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    setup.create_db(recreate_db=args.recreate_db)
    setup.create_table()
    add_data.add_afg_pop_data()
