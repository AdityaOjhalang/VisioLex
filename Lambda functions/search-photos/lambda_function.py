import json
import logging
import boto3
import random
from elasticsearch import Elasticsearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

headers = { "Content-Type": "application/json" }
region = 'us-east-1'
lex = boto3.client('lex-runtime', region_name=region)

def lambda_handler(event, context):
    q1 = event["q"]    
    labels = get_labels(q1)
    
    img_paths = []
    if labels:
        img_paths = get_photo_path(labels)
    
    if not img_paths:
        return {
            'statusCode': 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps('No Results found')
        }
    else:    
        return {
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps({
                'imagePaths': img_paths,
                'userQuery': q1,
                'labels': labels,
            }),
            'isBase64Encoded': False
        }
    
def get_labels(query):
    sample_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    userid = ''.join(random.choice(sample_string) for x in range(8))
    
    response = lex.post_text(
        botName='YourBotName',  # Replace with your bot name
        botAlias='YourBotAlias',  # Replace with your bot alias
        userId=userid,           
        inputText=query
    )
    
    labels = []
    if 'slots' in response:
        for key, value in response['slots'].items():
            if value:
                labels.append(value)
    return labels

def get_photo_path(keys):
    host = 'your_opensearch_host'  # Replace with your OpenSearch Service domain endpoint
    s = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=('adi-photos', 'Pass@word1'),  # Replace with your OpenSearch username and password
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    resp = []
    for key in keys:
        if key:
            searchData = s.search(index="photos", body={"query": {"match": {"labels": key}}})
            resp.append(searchData)

    output = []
    for r in resp:
        if 'hits' in r:
            for val in r['hits']['hits']:
                key = val['_source']['objectKey']
                if key not in output:
                    output.append('s3://your-bucket-name/' + key)  # Replace with your S3 bucket name
    return output
