import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json
import logging
import os

logger = logging.getLogger(__name__)


def create_s3_client(aws_access_key, aws_secret_key, aws_region):
    """Create S3 client - uses IAM role in Lambda, explicit credentials elsewhere"""

    # Check if we're running in AWS Lambda
    lambda_function_name = os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    execution_env = os.getenv("AWS_EXECUTION_ENV")
    is_lambda = lambda_function_name is not None or execution_env is not None

    try:
        if is_lambda:
            # Lambda environment - use IAM role (no explicit credentials)
            logger.info("🔒 Running in AWS Lambda - using IAM role for S3 access")
            session = boto3.Session()

            if aws_region:
                logger.info(f"🌍 Using specified region: {aws_region}")
                client = session.client("s3", region_name=aws_region)
            else:
                logger.info("🌍 Using default region detection")
                client = session.client("s3")

            return client

        elif (
            aws_access_key
            and aws_secret_key
            and aws_access_key.strip()
            and aws_secret_key.strip()
        ):
            # Local/GitHub Actions with explicit credentials
            logger.info("🔑 Using explicit AWS credentials")
            client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region,
            )
            return client
        else:
            # Try default credential chain
            logger.info("🔒 Using default AWS credential chain")
            session = boto3.Session()
            if aws_region:
                client = session.client("s3", region_name=aws_region)
            else:
                client = session.client("s3")
            return client

    except Exception as e:
        logger.error(f"❌ Error creating S3 client: {e}")
        raise


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
        return True

    except (NoCredentialsError, ClientError) as e:
        logger.error(f"❌ Failed to upload to S3: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error uploading to S3: {e}")
        return False
