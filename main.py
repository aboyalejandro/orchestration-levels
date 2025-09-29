import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.piwik import get_token, extract_endpoint
from src.s3 import create_s3_client, upload_to_s3
from src.local import save_local, get_args

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

auth_url = os.getenv("AUTH_URL")
base_url = os.getenv("BASE_URL")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
website_id = os.getenv("WEBSITE_ID")

# S3 configuration
s3_bucket = os.getenv("S3_BUCKET")
aws_region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")

# In Lambda, don't use explicit credentials - let IAM role handle it
is_lambda = (
    os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
    or os.getenv("AWS_EXECUTION_ENV") is not None
)

if is_lambda:
    # In Lambda, use IAM role (no explicit credentials)
    aws_access_key = None
    aws_secret_key = None
else:
    # Only in non-Lambda environments (local, GitHub Actions)
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")


def main():
    local_mode = get_args().local

    # Define date range - process each day from 2021-01-01 to 2021-01-31
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2021, 1, 31)

    # Create S3 client only if not in local mode
    s3_client = (
        None
        if local_mode
        else create_s3_client(aws_access_key, aws_secret_key, aws_region)
    )

    # Get token
    token = get_token(auth_url, client_id, client_secret)

    # Log storage mode
    storage_mode = "local /piwik-data directory" if local_mode else "S3"
    logger.info(f"🗂️  Storage mode: {storage_mode}")

    # Extract data from all endpoints
    endpoints = ["sessions", "events", "query"]

    # Iterate through each day in the date range
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")

        logger.info(f"📅 Processing data for {date_str}...")
        logger.info(f" ")

        for endpoint in endpoints:
            logger.info(f"- 🔍 Extracting {endpoint} for {date_str}...")
            data = extract_endpoint(
                base_url, endpoint, token, website_id, date_str, date_str
            )

            # Save data either locally or to S3
            if local_mode:
                local_path = f"piwik-data/{year}/{month}/{day}/{endpoint}.json"
                save_local(data, local_path)
            else:
                s3_key = f"piwik-data/{year}/{month}/{day}/{endpoint}.json"
                upload_to_s3(s3_client, s3_bucket, data, s3_key)

        # Move to next day
        current_date += timedelta(days=1)

    logger.info("🎉 ETL completed successfully!")


if __name__ == "__main__":
    main()
