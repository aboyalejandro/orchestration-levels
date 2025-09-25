import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json
import logging

logger = logging.getLogger(__name__)


def create_s3_client(aws_access_key, aws_secret_key, aws_region):
    """Create S3 client"""
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


def upload_to_s3(s3_client, s3_bucket, data, s3_key):
    """Upload JSON data directly to S3 bucket"""
    if not s3_bucket:
        logger.warning("⚠️  No S3 bucket configured, skipping S3 upload")
        return False

    try:
        json_data = json.dumps(data, indent=2)

        s3_client.put_object(
            Bucket=s3_bucket, Key=s3_key, Body=json_data, ContentType="application/json"
        )
        logger.info(f"- ☁️  Uploaded data to s3://{s3_bucket}/{s3_key}")
        logger.info(f"")
        return True

    except (NoCredentialsError, ClientError) as e:
        logger.error(f"❌ Failed to upload to S3: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error uploading to S3: {e}")
        return False
