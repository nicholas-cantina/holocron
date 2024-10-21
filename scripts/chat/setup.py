import subprocess
import psycopg2


def _initialize_tables(sql_file_path, params):
    with open(sql_file_path, "r", encoding="utf-8") as file:
        sql_commands = file.read()

    try:
        connection = psycopg2.connect(**params)
        with connection.cursor() as cursor:
            cursor.execute(sql_commands)
            connection.commit()
    except Exception as error:
        if connection:
            connection.rollback()
        raise error


def initialize_data_stores(config_data):
    db_params = config_data["database"]["params"]

    _initialize_tables(config_data["database"]["sql_file"], db_params)
