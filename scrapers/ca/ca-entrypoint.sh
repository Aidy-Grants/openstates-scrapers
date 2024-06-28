#!/bin/bash

# if [[ -z $1 ]]; then
#     echo "Missing argument for scrape type"
#     exit 1
# fi
set -e

START_DATE=${START_DATE}

echo "Starting entrypoint script..."

echo "Setting up MySQL host..."
MYSQL_HOST_IP=$(tail -n 1 /etc/hosts | awk '{print $1}')
echo "$MYSQL_HOST_IP mysql" >> /etc/hosts
echo "MySQL host set up."

# Wait for the MySQL server to be ready
echo "Checking if MySQL server is ready..."
while ! mysqladmin ping -h"$MYSQL_HOST" --silent; do
    echo "Waiting for MySQL server to be ready..."
    sleep 2
done
echo "MySQL server is ready."

# Run the ca-download task
echo "Running ca-download task..."
/opt/openstates/openstates/scrapers/ca/download.sh

# Check if the download script was successful
if [ $? -ne 0 ]; then
  echo "ca-download failed"
  exit 1
fi
echo "ca-download completed successfully."

# Run the scrape task
# poetry run os-update ca $1
echo "Running scrape task with poetry..."
poetry run os-update ca bills --fastmode --scrape
echo "Scrape task started."

echo "S3 upload"
python upload_to_s3.py ca --start_date $START_DATE
# if [[ -z $1 ]]; then
#     echo "Missing argument for scrape type"
#     exit 1
# fi
# set -e

# mysqld --user root --max_allowed_packet=512M &
# /opt/openstates/openstates/scrapers/ca/download.sh
# poetry run os-update ca $1
