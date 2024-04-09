import json
import boto3
import time
from elasticsearch import Elasticsearch, RequestsHttpConnection

def lambda_handler(event, context):
    # Record the start time of the Lambda function
    start_time = time.time()
    
    # Extract bucket name and photo key from the event
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        photo_key = event['Records'][0]['s3']['object']['key']
        photo_id = photo_key.split('/')[-1]  # Assuming the photo ID is the filename
        print(f"Photo upload detected: {photo_id} with key {photo_key} in bucket {bucket}")
        
        # Initialize boto3 client for Rekognition
        rekognition_client = boto3.client('rekognition')
        
        # Get the image from S3
        s3_client = boto3.client('s3')
        s3_response_time = time.time()
        s3_clientobj = s3_client.get_object(Bucket=bucket, Key=photo_key)
        s3_time_taken = time.time() - s3_response_time
        image = s3_clientobj['Body'].read()
        print(f"Time taken to retrieve image from S3: {s3_time_taken:.2f} seconds")
        
        # Detect labels in the image using Rekognition
        rekognition_response_time = time.time()
        rekognition_response = rekognition_client.detect_labels(
            Image={'Bytes': image},
            MaxLabels=10,
            MinConfidence=80
        )
        rekognition_time_taken = time.time() - rekognition_response_time
        labels = rekognition_response['Labels']
        custom_labels = [label['Name'] for label in labels]
        print(f"Detected labels for {photo_id}: {custom_labels}")
        print(f"Time taken for Rekognition to detect labels: {rekognition_time_taken:.2f} seconds")

        # Elasticsearch (OpenSearch Service) host information
        host = "search-photos-uxtdbraw4w3bibpqjm4lypa6x4.us-east-1.es.amazonaws.com"  # replace with your OpenSearch domain endpoint
        es_index = "photos"
        
        # Prepare the document as per the specified schema
        timeStamp = time.time()  # Fixed variable name to be consistent
        print(f"Processing complete at timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(timeStamp))}")
        document = {
            'objectKey': photo_key,
            'bucket': bucket,
            'createdTimestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timeStamp)),
            'labels': custom_labels
        }
        
        # Initialize Elasticsearch client
        es = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=('adi-photos', 'Pass@word1'),  # replace with your OpenSearch username and password, if applicable
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        # Index the document in Elasticsearch
        es_response_time = time.time()
        es.index(index=es_index, body=document)
        es_time_taken = time.time() - es_response_time
        print(f"Document indexed in Elasticsearch, took {es_time_taken:.2f} seconds")

    except Exception as e:
        print(f"Error processing file {photo_id} from bucket {bucket}. Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing file {photo_id}. Error: {str(e)}")
        }
    
    # Calculate the total Lambda execution time
    total_execution_time = time.time() - start_time
    print(f"Total execution time for processing {photo_id}: {total_execution_time:.2f} seconds")

    # Log the time when the processing is complete
    print(f"Processing complete at timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(timeStamp))}")
    
    # Return success status code and the labels detected
    return {
        'statusCode': 200,
        'body': json.dumps({
            'objectKey': photo_key,
            'bucket': bucket,
            'createdTimestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timeStamp)),
            'labels': custom_labels
        })
    }
