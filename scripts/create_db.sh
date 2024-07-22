#!/bin/bash

# Define the data directory
DATA_DIR="../data/db"

# Create the data directory if it doesn't exist
mkdir -p $DATA_DIR

# Initialize the PostgreSQL data directory
initdb $DATA_DIR

# Start the PostgreSQL service with the new data directory
pg_ctl -D $DATA_DIR -l logfile start

# Wait for a few seconds to ensure PostgreSQL service has started
sleep 5

# Define the database name
DB_NAME="memories"

# Get the current user
USER=$(whoami)

# Create the database and grant privileges
psql -D $DATA_DIR -U postgres -c "CREATE DATABASE $DB_NAME;"
psql -D $DATA_DIR -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $USER;"

echo "Database '$DB_NAME' created and privileges granted to user '$USER'."