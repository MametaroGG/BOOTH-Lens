import os
import boto3
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_r2_bucket():
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    bucket_name = os.getenv("R2_BUCKET_NAME")
    endpoint_url = os.getenv("R2_ENDPOINT_URL")
    access_key = os.getenv("R2_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")

    if not all([bucket_name, endpoint_url, access_key, secret_key]):
        logging.error("Missing R2 configuration in .env")
        return

    s3 = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto'
    )

    logging.info(f"Starting to clear all objects from bucket: {bucket_name}")
    
    # Paginate through all objects and delete them
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name)

    delete_batch = []
    total_deleted = 0
    
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                delete_batch.append({'Key': obj['Key']})
                
                if len(delete_batch) >= 1000:
                    s3.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_batch})
                    total_deleted += len(delete_batch)
                    logging.info(f"Deleted {total_deleted} objects...")
                    delete_batch = []

    if delete_batch:
        s3.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_batch})
        total_deleted += len(delete_batch)
        logging.info(f"Deleted {total_deleted} objects...")

    logging.info(f"Successfully cleared bucket {bucket_name}. Total objects deleted: {total_deleted}")

if __name__ == "__main__":
    clear_r2_bucket()
