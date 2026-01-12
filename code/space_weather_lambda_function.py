import urllib.request
import json
import boto3

# config:
API_KEY = "ZoIR3ASieEkYkcd02Cj7Jx2TMxqwJxh6hFekHvUk"  
url = f"https://api.nasa.gov/DONKI/GST?startDate=yyyy-MM-dd&endDate=yyyy-MM-dd&api_key={API_KEY}"

DESTINATION_BUCKET = "satellite-protector-bucket-yzu8r3"
DESTINATION_FOLDER = "raw_nasa_donki_weather/"

def lambda_handler(event, context):
    
    try:
        # Fetch the space weather data
        with urllib.request.urlopen(url) as response:
            if response is not None:
                data = json.loads(response.read().decode())
            else:
                raise ValueError("No response received from the API")

        latest_data = data[0]
        magnetic_field = latest_data.get('bt', 'N/A')
        
        print(f"Latest Magnetic Field Data: {magnetic_field}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Space weather data processed successfully!')
        }
    
    except Exception as e:
        print(f"Error fetching or processing space weather data, specifically: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing space weather data.')
        }