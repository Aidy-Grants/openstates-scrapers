#!/bin/bash
set -e

# Access the STATE, START_DATE, and RUN_SECONDS environment variables
STATE=${STATE}
START_DATE=${START_DATE}
RUN_SECONDS=${RUN_SECONDS}  # Accept the run-seconds parameter as the first argument

# If you need to ensure that the variables are not empty, you can check and provide defaults
# Uncomment the lines below to set default values if not provided
# STATE=${STATE:-default_state_value}
# START_DATE=${START_DATE:-$(date +%Y-%m-%d)}

echo "Processing for state: $STATE"

# Echo the contents of the current directory
echo "Contents of current directory:"
ls ./

# Check if run-seconds is provided
if [[ ! -z "$RUN_SECONDS" ]]; then
    # Run poetry command in the background
    poetry run os-update "$STATE" bills --fastmode --scrape &
    POETRY_PID=$!

    # Sleep for the specified number of seconds before killing the process
    sleep "$RUN_SECONDS"

    # Check if the process is still running and kill it if so
    if kill -0 $POETRY_PID 2>/dev/null; then
        echo "The poetry command is still running after $RUN_SECONDS seconds, killing it now..."
        kill -9 $POETRY_PID
    fi
else
    # Run poetry command normally (foreground)
    poetry run os-update "$STATE" bills --fastmode --scrape
fi

# Proceed with the rest of the script
echo "Running the scraper from $START_DATE to today"

# Debugging: Check if _data/STATE directory exists
if [ -d "./_data/$STATE" ]; then
    echo "Contents of _data/$STATE directory:"
    ls ./_data/$STATE
else
    echo "Directory ./_data/$STATE does not exist."
    exit 1
fi

# Check if there are any files starting with 'bill_' or 'vote_event_' in _data/STATE
bill_files=$(ls ./_data/$STATE/bill_* 2> /dev/null || echo "")
vote_event_files=$(ls ./_data/$STATE/vote_event_* 2> /dev/null || echo "")

# Debugging: Print matched files

if [ -n "$bill_files" ] || [ -n "$vote_event_files" ]; then
    echo "Files found. Proceeding with S3 upload"
    echo "S3 upload"
    python upload_to_s3.py $STATE --start_date $START_DATE
else
    echo "No files found that match the criteria. Skipping S3 upload."
fi
