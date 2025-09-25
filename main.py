#!/usr/bin/env python3
"""
Minimal Piwik ETL - Extract data and save as JSON files locally
Usage: python main.py --date 2021-01-01
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from piwik import get_token, extract_endpoint
from s3 import create_s3_client, upload_to_s3

load_dotenv()

auth_url = os.getenv("AUTH_URL")
base_url = os.getenv("BASE_URL")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
website_id = os.getenv("WEBSITE_ID")

# S3 configuration (environment variables only)
s3_bucket = os.getenv("S3_BUCKET")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")


def main():
    # Define date range - process each day from 2021-01-01 to 2021-01-31
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2021, 1, 31)

    # Create S3 client
    s3_client = create_s3_client(aws_access_key, aws_secret_key, aws_region)

    # Get token
    token = get_token(auth_url, client_id, client_secret)

    # Extract data from all endpoints
    endpoints = ["sessions", "events", "analytics"]

    # Iterate through each day in the date range
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")

        print(f"Processing data for {date_str}...")

        for endpoint in endpoints:
            print(f"  Extracting {endpoint} for {date_str}...")
            data = extract_endpoint(
                base_url, endpoint, token, website_id, date_str, date_str
            )

            # Upload directly to S3 with date partitioning
            s3_key = f"piwik-data/{year}/{month}/{day}/{endpoint}.json"
            upload_to_s3(s3_client, s3_bucket, data, s3_key)

        # Move to next day
        current_date += timedelta(days=1)

    print(f"ETL completed")


if __name__ == "__main__":
    main()
