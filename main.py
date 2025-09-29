import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json
import logging
import os

logger = logging.getLogger(__name__)


def create_s3_client(aws_access_key, aws_secret_key, aws_region):
    """Create S3 client - uses IAM role in Lambda, explicit credentials elsewhere"""

    print("🔍 DEBUG: create_s3_client() called")
    print(f"🔍 DEBUG: aws_access_key = {'***PRESENT***' if aws_access_key else 'None'}")
    print(f"🔍 DEBUG: aws_secret_key = {'***PRESENT***' if aws_secret_key else 'None'}")
    print(f"🔍 DEBUG: aws_region = {aws_region}")

    # Check if we're running in AWS Lambda
    lambda_function_name = os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    execution_env = os.getenv("AWS_EXECUTION_ENV")

    print(f"🔍 DEBUG: AWS_LAMBDA_FUNCTION_NAME = {lambda_function_name}")
    print(f"🔍 DEBUG: AWS_EXECUTION_ENV = {execution_env}")

    is_lambda = lambda_function_name is not None or execution_env is not None
    print(f"🔍 DEBUG: is_lambda = {is_lambda}")

    try:
        if is_lambda:
            # Lambda environment - use IAM role (no explicit credentials)
            print("🔒 Running in AWS Lambda - using IAM role for S3 access")

            # Create a new session with no explicit credentials
            session = boto3.Session()
            print("🔍 DEBUG: boto3.Session() created")

            if aws_region:
                print(f"🌍 Using specified region: {aws_region}")
                client = session.client("s3", region_name=aws_region)
            else:
                print("🌍 Using default region detection")
                client = session.client("s3")

            print("🔍 DEBUG: S3 client created with IAM role")
            return client

        elif (
            aws_access_key
            and aws_secret_key
            and aws_access_key.strip()
            and aws_secret_key.strip()
        ):
            # Local/GitHub Actions with explicit credentials
            print("🔑 Using explicit AWS credentials")
            client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region,
            )
            print("🔍 DEBUG: S3 client created with explicit credentials")
            return client
        else:
            # Try default credential chain
            print("🔒 Using default AWS credential chain")
            session = boto3.Session()
            if aws_region:
                client = session.client("s3", region_name=aws_region)
            else:
                client = session.client("s3")
            print("🔍 DEBUG: S3 client created with default credential chain")
            return client

    except Exception as e:
        print(f"❌ Error creating S3 client: {e}")
        import traceback

        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise


def upload_to_s3(s3_client, s3_bucket, data, s3_key):
    """Upload JSON data directly to S3 bucket"""

    print("🔍 DEBUG: upload_to_s3() called")
    print(f"🔍 DEBUG: s3_bucket = {s3_bucket}")
    print(f"🔍 DEBUG: s3_key = {s3_key}")
    print(f"🔍 DEBUG: data type = {type(data)}")

    if not s3_bucket:
        print("⚠️  No S3 bucket configured, skipping S3 upload")
        return False

    try:
        print("🔍 DEBUG: Converting data to JSON...")
        json_data = json.dumps(data, indent=2)
        print(f"🔍 DEBUG: JSON data size: {len(json_data)} characters")

        print("🔍 DEBUG: Calling s3_client.put_object()...")
        response = s3_client.put_object(
            Bucket=s3_bucket, Key=s3_key, Body=json_data, ContentType="application/json"
        )
        print(f"🔍 DEBUG: put_object() response: {response}")
        print(f"- ☁️  Uploaded data to s3://{s3_bucket}/{s3_key}")
        return True

    except (NoCredentialsError, ClientError) as e:
        print(f"❌ Failed to upload to S3: {e}")
        import traceback

        print(f"❌ Full traceback: {traceback.format_exc()}")
        return False
    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
        import traceback

        print(f"❌ Full traceback: {traceback.format_exc()}")
        return False
