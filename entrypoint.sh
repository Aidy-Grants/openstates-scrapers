#!/bin/bash
set -e

# Access the STATE and START_DATE environment variables
STATE=${STATE}
START_DATE=${START_DATE}

# If you need to ensure that the variables are not empty, you can check and provide defaults
# Uncomment the lines below to set default values if not provided
# STATE=${STATE:-default_state_value}
# START_DATE=${START_DATE:-$(date +%Y-%m-%d)}

echo "Processing for state: $STATE"
# Run poetry command in the background
poetry run os-update "$STATE" bills --fastmode --scrape &
POETRY_PID=$!

# Set a timeout for 60 seconds (1 minute)
sleep 60

# Check if the process is still running and kill it if so
if kill -0 $POETRY_PID 2>/dev/null; then
    echo "The poetry command is still running after 1 minute, killing it now..."
    kill -9 $POETRY_PID
fi

# Proceed with the rest of the script
echo "Running the scraper from $START_DATE to today"

echo "S3 upload"
python upload_to_s3.py $STATE --start_date $START_DATE
