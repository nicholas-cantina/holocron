#!/bin/bash

# Define the data directory
DATA_DIR="../data/db"

# Define the logfile location
LOG_FILE="../data/db/logfile"

# PostgreSQL credentials
DB_NAME="holocron"
DB_USER=$(whoami)
DB_HOST="localhost"
DB_PORT="5432"

# Change to the directory where the script is located
cd "$(dirname "$0")"

stop_postgres() {
  if pg_ctl -D $DATA_DIR status > /dev/null 2>&1; then
    stop_postgres
  fi
}

close_connections() {
  psql -h "$DB_HOST" -p "$DB_PORT" -d postgres -U "$DB_USER" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';"
}

# Function to drop the PostgreSQL database
drop_database() {
  psql -h "$DB_HOST" -p "$DB_PORT" -d postgres -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;"
}

# Function to stop PostgreSQL service if it's running
stop_postgres() {
  pg_ctl -D $DATA_DIR stop
}

# Function to delete the data directory
delete_data_dir() {
  rm -rf $DATA_DIR
}

# Function to delete the log file
delete_log_file() {
  rm -f $LOG_FILE
}


# Delete the data directory and log file
echo "Deleting data directory and log file..."
stop_postgres
close_connections
drop_database
delete_data_dir
delete_log_file
echo "Data directory and log file deleted."

echo "Cleanup complete."