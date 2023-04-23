from aws_xray_sdk.core import patch_all
patch_all()

import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MAILTABLE'])

def lambda_handler(event, context):
    for rec in event['Records']:
        message = rec['Sns']['Message']
        data = json.loads(message)
        if data['notificationType'] == 'Bounce':
            bounces = data['bounce']['bouncedRecipients']
            for bounce in bounces:
                email = bounce['emailAddress']
                response = table.update_item(
                    Key={'email': email},
                    UpdateExpression='set haserror=:val',
                    ExpressionAttributeValues={
                        ':val': 1
                    }
                )