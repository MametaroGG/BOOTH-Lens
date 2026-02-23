import boto3
import os
from dotenv import load_dotenv

load_dotenv('e:/GitHub/BOOTH-Lens/backend/.env')

client = boto3.client(
    's3',
    endpoint_url=os.getenv('R2_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY')
)

try:
    response = client.list_objects_v2(Bucket=os.getenv('R2_BUCKET_NAME'), MaxKeys=20)
    if 'Contents' in response:
        print("Recent items in R2 bucket:")
        # Sort by LastModified descending
        items = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        for obj in items[:10]:
            print(f"- {obj['Key']} (Size: {obj['Size']} bytes, LastModified: {obj['LastModified']})")
    else:
        print("Bucket is empty or no contents found.")
except Exception as e:
    print(f"Error accessing bucket: {e}")
