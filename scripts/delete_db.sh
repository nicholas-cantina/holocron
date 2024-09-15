#!/bin/bash

# Define the data directory
DATA_DIR="../data/db"

# Define the logfile location
LOG_FILE="../data/db/logfile"

# PostgreSQL credentials
DB_NAME="${DB_NAME:-holocron}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5234}"

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Function to stop any PostgreSQL service running on the specified port
stop_postgres_on_port() {
    echo "Attempting to stop PostgreSQL service running on port $DB_PORT..."
    local pids=$(lsof -ti :$PORT)
    local found=0

    if [ -z "$pids" ]; then
        echo "No processes found listening on port $PORT"
        return
    fi

    for pid in $pids; do
        if ps -p $pid -o comm= | grep -q postgres; then
            found=1
            command=$(ps -p $pid -o command=)
            echo "Found PostgreSQL process on port $PORT:"
            echo "PID:$pid"
            echo "Command:$command"
            
            if [ "$KILL_FLAG" = "kill" ]; then
                echo "Killing process $pid"
                kill -9 $pid
                if [ $? -eq 0 ]; then
                    echo "Successfully killed process $pid"
                else
                    echo "Failed to kill process $pid"
                fi
            fi
        fi
    done

    if [ $found -eq 0 ]; then
        echo "No PostgreSQL processes found on port $PORT"
    fi
}

# Function to stop the PostgreSQL service if it's running
stop_postgres() {
  echo "Attempting to stop PostgreSQL service..."
  if pg_ctl -D "$DATA_DIR" status > /dev/null 2>&1; then
    echo "  Stopping PostgreSQL service..."
    pg_ctl -D "$DATA_DIR" stop -m immediate || echo "Failed to stop PostgreSQL service."
  else
    echo "  PostgreSQL service is not running."
  fi
}

# Function to close all connections to the specified database
close_connections() {
  echo "Attempting to close connections to the database '$DB_NAME'..."
  if psql -h "$DB_HOST" -p "$DB_PORT" -d postgres -U "$DB_USER" -c "SELECT 1" >/dev/null 2>&1; then
    psql -h "$DB_HOST" -p "$DB_PORT" -d postgres -U "$DB_USER" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';" >/dev/null 2>&1
    echo "  Connections to the database '$DB_NAME' have been closed."
  else
    echo "  Unable to connect to PostgreSQL. The database might not be running."
  fi
}

# Function to drop the PostgreSQL database
drop_database() {
  echo "Attempting to drop database '$DB_NAME'..."
  if psql -h "$DB_HOST" -p "$DB_PORT" -d postgres -U "$DB_USER" -c "SELECT 1" >/dev/null 2>&1; then
    if psql -h "$DB_HOST" -p "$DB_PORT" -d postgres -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;" >/dev/null 2>&1; then
      echo "  Database '$DB_NAME' has been dropped."
    else
      echo "  Database '$DB_NAME' does not exist or has already been dropped."
    fi
  else
    echo "  Unable to connect to PostgreSQL. The database might not be running."
  fi
}

# Function to delete the data directory
delete_data_dir() {
  echo "Attempting to delete '$DATA_DIR'..."
  if [ -d "$DATA_DIR" ]; then
    echo "  Deleting data directory..."
    if rm -rf "$DATA_DIR"; then
      echo "  Data directory has been deleted."
    else
      echo "  Failed to delete data directory. It might be in use or you may not have sufficient permissions."
    fi
  else
    echo "  Data directory does not exist."
  fi
}

# Function to delete the log file
delete_log_file() {
  echo "Attempting to delete log file '$LOG_FILE'..."
  if [ -f "$LOG_FILE" ]; then
    echo "  Deleting log file..."
    if rm -f "$LOG_FILE"; then
      echo "  Log file has been deleted."
    else
      echo "  Failed to delete log file. It might be in use or you may not have sufficient permissions."
    fi
  else
    echo "  Log file does not exist."
  fi
}

# Execute cleanup steps
echo "Starting cleanup..."
stop_postgres_on_port
stop_postgres
close_connections
drop_database
delete_data_dir
delete_log_file

echo "Cleanup complete."