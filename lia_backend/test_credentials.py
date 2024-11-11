from google.cloud import storage
import os
from datetime import datetime

def test_credentials():
    try:
        # Print the path to verify it's set
        print(f"Credentials path: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
        
        # Try to create a client
        storage_client = storage.Client()
        
        # List buckets to verify access
        buckets = list(storage_client.list_buckets())
        print("Successfully authenticated! Found {} buckets.".format(len(buckets)))
        
        # Print bucket names
        for bucket in buckets:
            print(bucket.name)
        
        # Test upload to lia_resumes bucket
        bucket_name = "lia_resumes"  # or any other bucket from your list
        bucket = storage_client.bucket(bucket_name)
        
        # Create a test file
        test_content = "This is a test file to verify upload capabilities."
        blob_name = f"test_upload_{datetime.now().isoformat()}.txt"
        blob = bucket.blob(blob_name)
        
        # Upload the test content
        blob.upload_from_string(test_content)
        print(f"\nSuccessfully uploaded test file: {blob_name}")
        print(f"Public URL: {blob.public_url}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_credentials()