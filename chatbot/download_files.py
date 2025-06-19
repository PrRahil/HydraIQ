import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def download_s3_bucket(bucket_name, local_dir):
    try:
        # Initialize the S3 client with credentials
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        # List objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)

        if 'Contents' not in response:
            print(f"No files found in bucket {bucket_name}.")
            return

        # Ensure the local directory exists
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        # Download each file
        for obj in response['Contents']:
            file_key = obj['Key']
            local_file_path = os.path.join(local_dir, file_key)

            # Create local directories if necessary
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            print(f"Downloading {file_key} to {local_file_path}...")
            s3.download_file(bucket_name, file_key, local_file_path)

        print("Download completed successfully.")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")

# if _name_ == "_main_":
#     # Replace with your S3 bucket name and desired local directory
#     bucket_name = "abhi-bhingradiya-pvt"
#     local_directory = "./input"

#     download_s3_bucket(bucket_name, local_directory)