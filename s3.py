import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json


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


def upload_to_s3(s3_client, s3_bucket, data, s3_key):
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
