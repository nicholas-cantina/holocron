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

# Create the data directory if it doesn"t exist
mkdir -p $DATA_DIR

# Initialize the PostgreSQL data directory
initdb -D $DATA_DIR

# Start the PostgreSQL service with the new data directory
pg_ctl -D $DATA_DIR -l $LOG_FILE start

# Wait for a few seconds to ensure PostgreSQL service has started
sleep 5

# Create the database and grant privileges
psql -h "$DB_HOST" -p "$DB_PORT" -d postgres -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"
psql -h "$DB_HOST" -p "$DB_PORT" -d postgres -U "$DB_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $USER;"

echo "Database '$DB_NAME' created and privileges granted to user '$USER'."
