#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Define the data directory and logfile location
DATA_DIR="../data/db"
LOG_FILE="../data/db/logfile"

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

# Stop the PostgreSQL service
if pg_ctl -D $DATA_DIR status > /dev/null 2>&1; then
  echo "Stopping PostgreSQL service..."
  stop_postgres
  echo "PostgreSQL service stopped."
else
  echo "PostgreSQL service is not running."
fi

# Delete the data directory and log file
echo "Deleting data directory and log file..."
delete_data_dir
delete_log_file
echo "Data directory and log file deleted."

echo "Cleanup complete."