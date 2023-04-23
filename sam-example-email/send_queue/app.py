from aws_xray_sdk.core import patch_all
patch_all()

import json
import urllib.parse
import boto3
import os

from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['MAILTABLE'])
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=os.environ['QUEUENAME'])

    for rec in event['Records']:
        bucketname = rec['s3']['bucket']['name']
        filename = rec['s3']['object']['key']
        response = table.query(
            IndexName='haserror-index',
            KeyConditionExpression=Key('haserror').eq(0)
        )
        for item in response['Items']:
            table.update_item(
                Key={'email': item['email']},
                UpdateExpression="set issend=:val",
                ExpressionAttributeValues={
                    ':val': 0
                }
            )
            sqsresponse = queue.send_message(
                MessageBody=item['email'],
                MessageAttributes={
                    'username': {
                        'DataType': 'String',
                        'StringValue': item['username']
                    },
                    'bucketname': {
                        'DataType': 'String',
                        'StringValue': bucketname
                    },
                    'filename': {
                        'DataType': 'String',
                        'StringValue': filename
                    }
                }
            )
            print(json.dumps(sqsresponse))