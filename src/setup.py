import logging

from sqlalchemy import (
    Column,
    Date,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    text,
)

from src import settings, utils

logger = logging.getLogger(__name__)


def create_db(recreate_db: bool):
    # Create or recreate the DB
    temp_engine = create_engine(
        utils.get_connection_string(no_db_name=True),
        echo=True,
        isolation_level="AUTOCOMMIT",
    )
    with temp_engine.connect() as conn:
        if recreate_db:
            logger.info("DB exists and recreate is True, dropping current DB")
            conn.execute(text(f"DROP DATABASE IF EXISTS {settings.db_name};"))
        db_exists = conn.execute(
            text(
                f"SELECT datname FROM pg_database WHERE datname "
                f"= '{settings.db_name}';"
            )
        ).fetchone()
        if not db_exists:
            logger.info("DB does not exist, creating")
            conn.execute(text(f"CREATE DATABASE {settings.db_name};"))


def create_table():
    logger.info("Adding themes table")
    # Add the table
    engine = create_engine(
        utils.get_connection_string(),
        echo=True,
    )
    metadata = MetaData()
    Table(
        settings.table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("admin0_code_iso3", String),
        Column("admin1_name", String),
        Column("admin1_code", String),
        Column("admin2_name", String),
        Column("admin2_code", String),
        Column("start_date", Date),
        Column("end_date", Date),
        Column("record_id", Integer),
        Column("theme_name", String),
        Column("key", String),
        Column("value", String),
    )
    # Drop the table first in case it exists
    metadata.drop_all(engine, checkfirst=True)
    metadata.create_all(engine, checkfirst=True)
