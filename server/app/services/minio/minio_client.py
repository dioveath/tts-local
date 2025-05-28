import os
import json
from minio import Minio

minio_client = Minio(
    os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
    secure=os.environ.get("MINIO_SECURE", "False").lower() == "true",
)

minio_public_endpoint = os.environ.get("MINIO_PUBLIC_ENDPOINT", "http://localhost:9000")
bucket_name = os.environ.get("MINIO_BUCKET_NAME", "audio-storage")

print(f"Minio Public Endpoint: {minio_public_endpoint}")
print(f"Minio Bucket Name: {bucket_name}")

try:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                }
            ],
        }
        policy_str = json.dumps(policy)
        minio_client.set_bucket_policy(bucket_name, policy_str)
        print(f"Bucket '{bucket_name}' created and policy set.")
except Exception as e:
    print(f"Error creating bucket: {e}")
