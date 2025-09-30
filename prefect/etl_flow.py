"""
Prefect ETL Flow for Piwik Analytics Data
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from prefect import flow, task, get_run_logger
from prefect_aws import S3Bucket
from dotenv import load_dotenv

# Import existing modules
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.piwik import get_token, extract_endpoint

# Load environment variables
load_dotenv()


@task
def get_auth_token() -> str:
    """Get authentication token from Piwik API"""
    logger = get_run_logger()

    auth_url = os.getenv("AUTH_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    logger.info("🔑 Getting authentication token...")
    token = get_token(auth_url, client_id, client_secret)
    logger.info("✅ Token obtained successfully")
    return token


@task
def extract_data_for_endpoint(
    endpoint: str, token: str, date_str: str
) -> Dict[str, Any]:
    """Extract data from a single Piwik endpoint for a specific date"""
    logger = get_run_logger()

    base_url = os.getenv("BASE_URL")
    website_id = os.getenv("WEBSITE_ID")

    logger.info(f"🔍 Extracting {endpoint} data for {date_str}...")

    data = extract_endpoint(base_url, endpoint, token, website_id, date_str, date_str)

    logger.info(
        f"✅ Extracted {len(data) if isinstance(data, list) else 'N/A'} records from {endpoint}"
    )
    return {"endpoint": endpoint, "date": date_str, "data": data}


@task
def upload_to_s3_prefect(data_package: Dict[str, Any], s3_bucket: str) -> str:
    """Upload data to S3 using Prefect S3 utilities"""
    logger = get_run_logger()

    endpoint = data_package["endpoint"]
    date_str = data_package["date"]
    data = data_package["data"]

    # Convert date to path components
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")
    day = date_obj.strftime("%d")

    s3_key = f"piwik-data/{year}/{month}/{day}/{endpoint}.json"

    try:
        # Use Prefect S3Bucket block
        s3_bucket_block = S3Bucket.load("piwik-data-bucket")

        # Convert data to JSON bytes
        json_data = json.dumps(data, indent=2)
        json_bytes = json_data.encode("utf-8")

        # Upload to S3
        s3_bucket_block.write_path(path=s3_key, content=json_bytes)

        logger.info(f"☁️ Uploaded {endpoint} data to s3://{s3_bucket}/{s3_key}")
        return s3_key

    except Exception as e:
        logger.error(f"❌ Failed to upload {endpoint} to S3: {e}")
        raise


@task
def get_date_range(start_date: datetime, end_date: datetime) -> List[str]:
    """Generate list of date strings for the given range"""
    logger = get_run_logger()

    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    logger.info(
        f"📅 Generated {len(dates)} dates from {start_date.date()} to {end_date.date()}"
    )
    return dates


@flow(name="piwik-etl-flow")
def piwik_etl_flow(
    # Processing 3 days of data
    start_date: datetime = datetime(2021, 1, 1),
    end_date: datetime = datetime(2021, 1, 3),
):
    """
    Main Prefect flow for Piwik ETL process

    Args:
        start_date: Start date for data extraction
        end_date: End date for data extraction
    """
    logger = get_run_logger()

    # Configuration
    endpoints = ["sessions", "events", "query"]
    s3_bucket = os.getenv("S3_BUCKET")

    # Validate S3 configuration
    if not s3_bucket:
        logger.error("❌ S3_BUCKET not configured")
        raise ValueError("S3_BUCKET must be set for Prefect flow")

    logger.info(f"🗂️ Storage mode: S3 (bucket: {s3_bucket})")

    # Get authentication token
    token = get_auth_token()

    # Generate date range
    dates = get_date_range(start_date, end_date)

    # Process each date
    for date_str in dates:
        logger.info(f"📅 Processing data for {date_str}...")

        # Extract data from all endpoints for this date
        data_packages = []
        for endpoint in endpoints:
            data_package = extract_data_for_endpoint(endpoint, token, date_str)
            data_packages.append(data_package)

        # Upload to S3
        s3_keys = []
        for package in data_packages:
            s3_key = upload_to_s3_prefect(package, s3_bucket)
            s3_keys.append(s3_key)
        logger.info(f"☁️ Uploaded {len(s3_keys)} files to S3 for {date_str}")

    logger.info("🎉 ETL process completed successfully!")
    return f"Processed {len(dates)} dates with {len(endpoints)} endpoints each"


if __name__ == "__main__":
    # Run the flow locally
    result = piwik_etl_flow()
    print(f"Flow completed: {result}")
