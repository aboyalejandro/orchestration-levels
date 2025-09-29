"""
Setup Prefect S3 Block for the ETL flow
"""
import os
from prefect_aws import S3Bucket, AwsCredentials
from dotenv import load_dotenv

load_dotenv()

def setup_s3_block():
    """Create and save S3 bucket block for Prefect"""
    
    # Create AWS credentials block (optional - can use IAM roles)
    aws_credentials = None
    if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        aws_credentials = AwsCredentials(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        aws_credentials.save("aws-credentials", overwrite=True)
        print("✅ AWS credentials block created")
    
    # Create S3 bucket block
    s3_bucket_block = S3Bucket(
        bucket_name=os.getenv("S3_BUCKET"),
        aws_credentials=aws_credentials,  # None if using IAM roles
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
    
    s3_bucket_block.save("piwik-data-bucket", overwrite=True)
    print(f"✅ S3 bucket block 'piwik-data-bucket' created for bucket: {os.getenv('S3_BUCKET')}")

if __name__ == "__main__":
    setup_s3_block()