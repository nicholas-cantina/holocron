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


def _create_db(create_db_script_path, params):
    try:
        subprocess.run([create_db_script_path], 
                       check=True, 
                       capture_output=True,
                       text=True, 
                       env={
                           "DB_NAME": params["dbname"], 
                           "DB_USER": params["user"],
                           "DB_HOST": params["host"],
                           "DB_PORT": params["port"]
                       }
                   )
                       
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Script failed with error: {e.stderr}")


def initialize_data_stores(config_data):
    db_params = config_data["database"]["params"]

    _initialize_tables(config_data["database"]["sql_file"], db_params)
