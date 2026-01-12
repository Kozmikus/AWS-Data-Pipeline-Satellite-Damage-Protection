import urllib.request
import json
import boto3
from datetime import datetime

# Config:
API_KEY = "ZoIR3ASieEkYkcd02Cj7Jx2TMxqwJxh6hFekHvUk" # NOT SAFE TO HARD CODE IN PRODUCTION! 
# irl this should be stored in AWS Secrets Manager or as an encrypted environment variable
# for the sake of simplicity in this example I will hardcode it here

url = f"https://api.nasa.gov/DONKI/GST?startDate=yyyy-MM-dd&endDate=yyyy-MM-dd&api_key={API_KEY}"

DESTINATION_BUCKET = "satellite-protector-bucket-yzu8r3"
DESTINATION_FOLDER = "raw_nasa_donki_weather/"

def lambda_handler(event, context):
    
    try:
        # Fetching space weather data from NASA DONKI API
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                raise Exception(f"API fetching failed: {response.status} - {response.reason}")
            data = json.loads(response.data.decode('utf-8')) # decodes bytes to string before loading in JSON format

        if not data:
            raise Exception("No data retrieved from NASA API. Terminating execution.") # handling empty data case and raising an 
                                                                # exception for Lambda to capture and abort execution
        
        print(f"Successfully retrieved {len(data)} records from NASA API.")

        # Preparing the upload file to S3
        s3_client = boto3.client('s3')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"gst_data_{timestamp}.json"
        s3_path = f"{DESTINATION_FOLDER}{file_name}"

        # Uploading data to S3
        s3_client.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=s3_path,
            Body=json.dumps(data), # json.dumps to convert Python object back to JSON string
            ContentType='application/json'
        ) # uploading JSON data as a string and setting content type

        print(f"Data has been successfully uploaded to s3://{DESTINATION_BUCKET}/{s3_path}")

        return {
            'statusCode': 200,
            'body': json.dumps(f'Space weather data processed and uploaded successfully with {file_name} to s3://{DESTINATION_BUCKET}/{s3_path}.')
        }
    
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        raise e  # raise exception for AWS Lambda to capture the failure and abort execution