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
    

def initialize_db(create_db_script_path, sql_file_path, params):
    # Run the script to create the database and user
    try:
        subprocess.run([create_db_script_path], check=True, capture_output=True,
                       text=True, env={"DB_NAME": params["dbname"]})
                       
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Script failed with error: {e.stderr}")
    
    _initialize_tables(sql_file_path, params)


def delete_db(drop_db_script_path, params):
    # Run the script to delete the database
    try:
        subprocess.run([drop_db_script_path], check=True, capture_output=True,
                       text=True, env={"DB_NAME": params["dbname"]})
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Script failed with error: {e.stderr}")
