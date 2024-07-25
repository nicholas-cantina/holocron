#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Define the data directory
DATA_DIR="../data/db"

# Define the logfile location
LOG_FILE="../data/db/logfile"

# Define the database name
DB_NAME="holocron"

# Get the current user
USER=$(whoami)

# Create the data directory if it doesn't exist
mkdir -p $DATA_DIR

# Initialize the PostgreSQL data directory
initdb -D $DATA_DIR

# Start the PostgreSQL service with the new data directory
pg_ctl -D $DATA_DIR -l $LOG_FILE start

# Wait for a few seconds to ensure PostgreSQL service has started
sleep 5

# Create the database and grant privileges
psql -U $USER -d postgres -c "CREATE DATABASE $DB_NAME;"
psql -U $USER -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $USER;"

echo "Database '$DB_NAME' created and privileges granted to user '$USER'."
