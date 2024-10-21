#!/bin/bash

# Add to the path variables
export PATH=$PATH:/opt/homebrew/bin

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

# Create the data directory if it doesn't exist
mkdir -p "$DATA_DIR"

# Initialize the PostgreSQL data directory with DB_USER as superuser
if ! initdb -D "$DATA_DIR" --auth=trust --username="$DB_USER"; then
  echo "Failed to initialize the PostgreSQL data directory."
  exit 1
fi

# Modify postgresql.conf to use the specified port
sed -i.bak "s/^#port = 5432/port = $DB_PORT/" "$DATA_DIR/postgresql.conf"

# Start the PostgreSQL service with the new data directory and specified port
if ! pg_ctl -D "$DATA_DIR" -o "-p $DB_PORT" -l "$LOG_FILE" start; then
  echo "Failed to start PostgreSQL service."
  exit 1
fi

# Function to wait for PostgreSQL to start
wait_for_postgres() {
    local max_attempts=30
    local attempt=0
    while ! pg_isready -h $DB_HOST -p $DB_PORT -q; do
        attempt=$((attempt+1))
        if [ $attempt -eq $max_attempts ]; then
            echo "Error: PostgreSQL did not start within the expected time."
            exit 1
        fi
        sleep 1
    done
}

# Wait for PostgreSQL to start
wait_for_postgres

# Create the database
if ! createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -E UTF8 -T template0 "$DB_NAME"; then
  echo "Failed to create the database '$DB_NAME'."
  exit 1
fi

echo "Database '$DB_NAME' created successfully."

echo "PostgreSQL setup complete. Superuser '$DB_USER' can now access the database '$DB_NAME' on port $DB_PORT without a password."