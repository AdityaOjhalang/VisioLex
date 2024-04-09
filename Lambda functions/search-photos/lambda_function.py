import json
import logging
import boto3
import random
from elasticsearch import Elasticsearch, RequestsHttpConnection

# Configure logger to print the log messages
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # INFO level is typically suitable for production environments

headers = {"Content-Type": "application/json"}
region = 'us-east-1'
lex = boto3.client('lex-runtime', region_name=region)

def lambda_handler(event, context):
    logger.info(f'Event received: {event}')
    
    # Extract the 'Animal' slot value from the Lex event
    animal_slot = event['currentIntent']['slots'].get('Animal', '') if 'currentIntent' in event else ''
    
    labels = []
    if animal_slot:
        labels.append(animal_slot)

    img_paths = get_photo_path(labels) if labels else []

    if not img_paths:
        logger.info('No results found for the labels received.')
        response_body = 'No Results found'
    else:
        logger.info(f'Image paths found: {img_paths}')
        response_body = {
            'imagePaths': img_paths,
            'userQuery': animal_slot,
            'labels': labels,
        }

    return {
        'statusCode': 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        'body': json.dumps(response_body),
        'isBase64Encoded': False
    }

# Remove the get_labels function since it is no longer needed.

def get_photo_path(keys):
    host = 'search-photos-uxtdbraw4w3bibpqjm4lypa6x4.us-east-1.es.amazonaws.com'
    try:
        s = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=('adi-photos', 'Pass@word1'),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        resp = []
        for key in keys:
            searchData = s.search(index="photos", body={"query": {"match": {"labels": key}}})
            resp.append(searchData)
            logger.info(f'Search results for "{key}": {searchData}')

        output = []
        for r in resp:
            hits = r.get('hits', {}).get('hits', [])
            for val in hits:
                object_key = val['_source'].get('objectKey', '')
                if object_key and object_key not in output:
                    output.append(f's3://photos/{object_key}')

        return output

    except Exception as e:
        logger.error('Error during search in OpenSearch', exc_info=True)
        return []

