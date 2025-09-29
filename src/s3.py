import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json
import logging
import os

logger = logging.getLogger(__name__)


def create_s3_client(aws_access_key, aws_secret_key, aws_region):
    """Create S3 client - uses IAM role in Lambda, explicit credentials elsewhere"""

    # Debug logging
    logger.info("🔍 DEBUG: Environment variables:")
    logger.info(
        f"  - AWS_LAMBDA_FUNCTION_NAME: {os.getenv('AWS_LAMBDA_FUNCTION_NAME')}"
    )
    logger.info(f"  - AWS_EXECUTION_ENV: {os.getenv('AWS_EXECUTION_ENV')}")
    logger.info(f"  - AWS_REGION: {os.getenv('AWS_REGION')}")
    logger.info(f"  - AWS_DEFAULT_REGION: {os.getenv('AWS_DEFAULT_REGION')}")
    logger.info(f"  - Passed aws_access_key: {'***' if aws_access_key else 'None'}")
    logger.info(f"  - Passed aws_secret_key: {'***' if aws_secret_key else 'None'}")

    # Check if we're running in AWS Lambda
    is_lambda = (
        os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
        or os.getenv("AWS_EXECUTION_ENV") is not None
    )

    logger.info(f"🔍 DEBUG: is_lambda = {is_lambda}")

    if is_lambda:
        # Lambda environment - use IAM role (no explicit credentials)
        logger.info("🔒 Running in AWS Lambda - using IAM role for S3 access")

        # Explicitly unset AWS credential environment variables if they exist
        # This forces boto3 to use the IAM role
        session = boto3.Session()

        if aws_region:
            logger.info(f"🌍 Using specified region: {aws_region}")
            return session.client("s3", region_name=aws_region)
        else:
            logger.info("🌍 Using default region detection")
            return session.client("s3")

    elif (
        aws_access_key
        and aws_secret_key
        and aws_access_key.strip()
        and aws_secret_key.strip()
    ):
        # Local/GitHub Actions with explicit credentials
        logger.info("🔑 Using explicit AWS credentials")
        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
    else:
        # Try default credential chain (EC2 instance profile, etc.)
        logger.info("🔒 Using default AWS credential chain")
        session = boto3.Session()
        if aws_region:
            return session.client("s3", region_name=aws_region)
        else:
            return session.client("s3")


def upload_to_s3(s3_client, s3_bucket, data, s3_key):
    """Upload JSON data directly to S3 bucket"""
    if not s3_bucket:
        logger.warning("⚠️  No S3 bucket configured, skipping S3 upload")
        return False

    try:
        # Debug: Check what credentials the client is actually using
        try:
            credentials = s3_client._get_credentials()
            if credentials:
                logger.info(
                    f"🔍 DEBUG: S3 client using credentials: {credentials.access_key[:10]}***"
                )
            else:
                logger.info(
                    "🔍 DEBUG: S3 client has no credentials (should use IAM role)"
                )
        except Exception as e:
            logger.info(f"🔍 DEBUG: Could not inspect credentials: {e}")

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
