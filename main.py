#!/usr/bin/env python3
"""
Minimal Piwik ETL - Extract data and save as JSON files locally
Usage: python main.py --date 2021-01-01
"""

import requests
import json
import os
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

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


def get_token(auth_url, client_id, client_secret):
    """Get bearer token"""
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(auth_url, json=data)
    response.raise_for_status()
    return response.json()["access_token"]


def extract_endpoint(base_url, endpoint, token, website_id):
    """Extract data from Piwik endpoint"""
    url = f"{base_url}{endpoint}/"

    # Basic payload for all endpoints
    payload = {
        "website_id": website_id,
        "date_from": "2021-01-01",
        "date_to": "2021-03-30",
        "filters": {"operator": "and", "conditions": []},
        "offset": 0,
        "limit": 10000,
        "format": "json",
    }

    # Add endpoint-specific columns
    if endpoint == "sessions":
        payload["columns"] = [
            {"column_id": "visitor_session_number"},
            {"column_id": "visitor_returning"},
            {"column_id": "source_medium"},
            {"column_id": "campaign_name"},
            {"column_id": "session_goals"},
            {"column_id": "session_total_page_views"},
            {"column_id": "session_total_events"},
            {"column_id": "visitor_days_since_last_session"},
            {"column_id": "visitor_days_since_first_session"},
            {"column_id": "location_country_name"},
        ]
    elif endpoint == "events":
        payload["columns"] = [
            {"column_id": "event_index"},
            {"column_id": "page_view_index"},
            {"column_id": "custom_event_category"},
            {"column_id": "custom_event_action"},
            {"column_id": "custom_event_name"},
            {"column_id": "event_url"},
            {"column_id": "source_medium"},
            {"column_id": "campaign_name"},
            {"column_id": "goal_id"},
        ]
    else:  # query
        payload["columns"] = [
            {"transformation_id": "to_date", "column_id": "timestamp"},
            {"column_id": "referrer_type"},
            {"column_id": "source_medium"},
            {"column_id": "campaign_name"},
            {"column_id": "campaign_content"},
            {"column_id": "session_entry_url"},
            {"column_id": "visitor_returning"},
            {"column_id": "location_country_name"},
            {"column_id": "operating_system"},
            {"column_id": "device_type"},
            {"column_id": "location_city_name"},
            {"column_id": "events"},
            {"column_id": "visitors"},
            {"column_id": "sessions"},
            {"column_id": "page_views"},
            {"column_id": "ecommerce_conversions"},
            {"column_id": "cart_additions"},
            {"column_id": "ecommerce_abandoned_carts"},
            {"column_id": "consents_none"},
            {"column_id": "consents_full"},
        ]

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def create_s3_client(aws_access_key, aws_secret_key, aws_region):
    """Create S3 client"""
    # Create S3 client (uses env vars or IAM role in Lambda)
    if aws_access_key and aws_secret_key:
        # Local/GitHub Actions with explicit credentials
        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
    else:
        # Lambda/ECS with IAM role (no explicit credentials needed)
        return boto3.client("s3", region_name=aws_region)


def upload_to_s3(s3_client, data, s3_key):
    """Upload JSON data directly to S3 bucket"""
    if not s3_bucket:
        print("No S3 bucket configured, skipping S3 upload")
        return False

    try:
        # Convert data to JSON string
        json_data = json.dumps(data, indent=2)

        # Upload directly to S3
        s3_client.put_object(
            Bucket=s3_bucket, Key=s3_key, Body=json_data, ContentType="application/json"
        )
        print(f"Uploaded data to s3://{s3_bucket}/{s3_key}")
        return True

    except (NoCredentialsError, ClientError) as e:
        print(f"Failed to upload to S3: {e}")
        return False
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False


def main():
    # Create date-based folder structure: 2021/01/01/
    date_obj = datetime(2021, 1, 1)  # Using start date for folder structure
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")
    day = date_obj.strftime("%d")

    # Create S3 client
    s3_client = create_s3_client(aws_access_key, aws_secret_key, aws_region)

    # Get token
    token = get_token(auth_url, client_id, client_secret)

    # Extract data from all endpoints
    endpoints = ["sessions", "events", "query"]

    for endpoint in endpoints:
        print(f"Extracting {endpoint}...")
        data = extract_endpoint(base_url, endpoint, token, website_id)

        # Upload directly to S3 with date partitioning
        s3_key = f"piwik-data/{year}/{month}/{day}/{endpoint}.json"
        upload_to_s3(s3_client, data, s3_key)

    print(f"ETL completed")


if __name__ == "__main__":
    main()
