from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    text,
)

from src import settings

_RECREATE_DB = False

# Create or recreate the DB
temp_engine = create_engine(
    f"postgresql+psycopg2://{settings.username}:{settings.password}@{settings.host}:{settings.port}/",
    echo=True,
    isolation_level="AUTOCOMMIT",
)
with temp_engine.connect() as conn:
    if _RECREATE_DB:
        conn.execute(text(f"DROP DATABASE IF EXISTS {settings.db_name};"))
    db_exists = conn.execute(
        text(
            f"SELECT datname FROM pg_database WHERE datname "
            f"= '{settings.db_name}';"
        )
    ).fetchone()
    if not db_exists:
        conn.execute(text(f"CREATE DATABASE {settings.db_name};"))

# Add the table
engine = create_engine(
    f"postgresql+psycopg2://{settings.username}:{settings.password}@{settings.host}:{settings.port}/{settings.db_name}",
    echo=True,
)
metadata = MetaData()
my_table = Table(
    "themes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("age", Integer),
)
metadata.create_all(engine)

# with engine.connect() as conn:
#    result = conn.execute(text("select 'Hello World'"))
#    print(result.all())
