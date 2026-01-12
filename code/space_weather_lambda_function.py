import urllib.request
import json
import boto3
from datetime import datetime

# Config:
API_KEY = "ZoIR3ASieEkYkcd02Cj7Jx2TMxqwJxh6hFekHvUk" # NOT SAFE TO HARD CODE IN PRODUCTION! 
# irl this should be stored in AWS Secrets Manager or as an encrypted environment variable
# for the sake of simplicity in this example I will hardcode it here

DESTINATION_BUCKET = "satellite-protector-bucket-yzu8r3"

# Mapping of data types to S3 folders
DESTINATION_FOLDERS = {
    "GST": "raw_nasa_gst/",  # Geomagnetic Storms (The Impact), abbreviated as GST
    "FLR": "raw_nasa_flr/"   # Solar Flares (The Warning), abbreviated as FLR
}

def lambda_handler(event, context):
    
    results = []
    s3_client = boto3.client('s3') # initializing S3 client using boto3 to not do it twice in the loop
    today_str = datetime.now().strftime("%Y-%m-%d") # getting only today's date in yyyy-MM-dd format to use in API request
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"Starting data ingestion for date: {today_str}")

    for point, folder in DESTINATION_FOLDERS.items():
        
        try:
            # Fetching space weather data from NASA DONKI API
            url = f"https://api.nasa.gov/DONKI/{point}?startDate={today_str}&endDate={today_str}&api_key={API_KEY}" 
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    raise Exception(f"API fetching failed: {response.status} - {response.reason}")
                data = json.loads(response.read().decode('utf-8')) # decodes bytes to string before loading in JSON format

            if not data:
                print(f"No data retrieved from NASA API for endpoint {point} on date {today_str}.")
                results.append(f"{point}: No data today ({today_str}).")
                continue  # skipping to the next point if no data is returned

            print(f"Successfully retrieved {len(data)} records from NASA API for endpoint {point} on date {today_str}.")

            # Preparing the upload file to S3
            if point == "GST":
                file_name = f"nasa_gst_{timestamp}.json"
            elif point == "FLR":
                file_name = f"nasa_flr_{timestamp}.json"
            else:
                raise Exception(f"Unknown endpoint: {point}")
            s3_path = f"{folder}{file_name}"

            # Uploading data to S3
            s3_client.put_object(
                Bucket=DESTINATION_BUCKET,
                Key=s3_path,
                Body=json.dumps(data), # json.dumps to convert Python object back to JSON string
                ContentType='application/json'
            ) # uploading JSON data as a string and setting content type

            print(f"Data has been successfully uploaded to s3://{DESTINATION_BUCKET}/{s3_path}")
            results.append(f"Successfully uploaded {len(data)} records to {s3_path} in bucket {DESTINATION_BUCKET}.")
        
        except Exception as e:
            print(f"ERROR for {point}: {str(e)}")
            results.append(f"ERROR processing {point}: {str(e)}") # logging error message
            raise e  # raise exception for AWS to capture the failure and abort execution

    return {
        'statusCode': 200,
        'body': json.dumps(results) # returning results (both) as JSON string
    }