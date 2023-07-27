from src import settings


def get_connection_string(no_db_name: bool = False):
    connection_string = f"postgresql+psycopg2://{settings.username}:{settings.password}@{settings.host}:{settings.port}/"
    if not no_db_name:
        connection_string += f"{settings.db_name}"
    return connection_string
