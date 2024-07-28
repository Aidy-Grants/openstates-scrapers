import os
import json
import boto3
import signal
import argparse
from dateutil import parser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pytz


def parse_date(date_str):
    try:
        # Parse the date, assuming UTC if no timezone is specified
        parsed_date = parser.parse(date_str, fuzzy=True)
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=pytz.UTC)
        return parsed_date.date()
    except ValueError:
        print(f"Warning: Could not parse date '{date_str}'. Skipping.")
        return None


def upload_file(local_file_path, s3_client, bucket_name, s3_file_path, start_date=None):
    try:
        filename = os.path.basename(local_file_path)
        if start_date is not None and (
            filename.startswith("bill_") or filename.startswith("vote_event_")
        ):
            with open(local_file_path, "r") as file:
                data = json.load(file)
            if filename.startswith("bill_"):
                action_dates = [action["date"] for action in data.get("actions", [])]
            elif filename.startswith("vote_event_"):
                action_dates = [data.get("start_date")]

            if action_dates:
                parsed_dates = [
                    parse_date(d) for d in action_dates if parse_date(d) is not None
                ]
                if parsed_dates:
                    latest_date_parsed = max(parsed_dates)
                    start_date_parsed = parse_date(start_date) if start_date else None
                    print("LATEST", latest_date_parsed, "START", start_date_parsed)
                    if start_date_parsed and start_date_parsed <= latest_date_parsed:
                        print("UPLOADING")
                        # proceed with upload
                        s3_client.upload_file(
                            local_file_path, bucket_name, s3_file_path
                        )
                        print(
                            f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_file_path}"
                        )
                    else:
                        print(
                            f"Date requirements not met for {filename}. Latest date: {latest_date_parsed}, Start date: {start_date_parsed}. Skipping upload."
                        )
                        return
                else:
                    print(
                        f"No valid dates found in the file {filename}. Skipping upload."
                    )
                    return
            else:
                print(f"No action dates found in the file {filename}. Skipping upload.")
                return
        else:
            # If no date checking is required, proceed with upload
            s3_client.upload_file(local_file_path, bucket_name, s3_file_path)
            print(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_file_path}")
    except Exception as e:
        print(
            f"Error processing or uploading {local_file_path} to s3://{bucket_name}/{s3_file_path}: {e}"
        )


def main():
    parser = argparse.ArgumentParser(description="Upload files to an S3 bucket.")
    parser.add_argument(
        "--bucket_name",
        type=str,
        required=False,
        help="The name of the S3 bucket",
        default="aidy-persistent",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        required=False,
        help="Number of concurrent workers",
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default="2000-01-01",
        required=False,
        help="Only upload data after this date",
    )
    parser.add_argument("state", type=str, help="State for which to upload data")
    args = parser.parse_args()
    print("ARGS", args)

    # Handling the default for s3_folder_path after parsing
    today_date = datetime.now().strftime("%Y-%m-%d")
    if args.start_date is None:
        args.start_date = "2000-01-01"

    # Assuming s3_folder_path isn't strictly required as an argument
    args.s3_folder_path = f"state_scrapes/{args.start_date}_{today_date}/{args.state}"

    print(f"Uploading data for state {args.state} from")
    print(
        f"Uploading to bucket {args.bucket_name} at {args.s3_folder_path} with {args.workers} workers"
    )

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    local_folder_path = f"./_data/{args.state}"
    files_to_upload = []
    print("HERE")
    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_file_path = os.path.join(args.s3_folder_path, file).replace("\\", "/")
            print("LOCAL", local_file_path)
            print("S3", s3_file_path)
            files_to_upload.append(
                (
                    local_file_path,
                    s3_client,
                    args.bucket_name,
                    s3_file_path,
                    args.start_date,
                )
            )

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(upload_file, *file_args) for file_args in files_to_upload
        ]

        def shutdown(signal_received, frame):
            print("Shutdown signal received. Shutting down...")
            executor.shutdown(wait=True)
            print("All threads have been safely terminated.")
            exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error during upload: {e}")


if __name__ == "__main__":
    main()
