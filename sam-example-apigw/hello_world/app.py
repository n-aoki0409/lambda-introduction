import json
import boto3
import base64
import time
import decimal
import os

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
client = boto3.client('ses')

MAILFROM = os.environ['MAILFROM']
SEQUENCETABLE = os.environ['SEQUENCETABLE']
USERTABLE = os.environ['USERTABLE']
SAVEBUCKET = os.environ['SAVEBUCKET']

def send_email(to, subject, body):
    response = client.send_email(
        Source = MAILFROM,
        ReplyToAddresses = [MAILFROM],
        Destination = {
            'ToAddresses': [to]
        },
        Message = {
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )

def next_seq(table, tablename):
    response = table.update_item(
        Key={'tablename': tablename},
        UpdateExpression="set seq = seq + :val",
        ExpressionAttributeValues={':val': 1},
        ReturnValues='UPDATED_NEW'
    )
    return response['Attributes']['seq']

def lambda_handler(event, context):
    try:
        seqtable = dynamodb.Table(SEQUENCETABLE)
        nextseq = next_seq(seqtable, USERTABLE)
        
        body = event['body']
        if event['isBase64Encoded']:
            body = base64.b64decode(body)
            
        decoded = json.loads(body)
        username = decoded['username']
        email = decoded['email']
        host = event['requestContext']['http']['sourceIp']
        
        now = time.time()
        
        url = s3.generate_presigned_url(
            ClientMethod = 'get_object',
            Params = {'Bucket': SAVEBUCKET, 'Key': 'lambda.png'},
            ExpiresIn = 8 * 60 * 60,
            HttpMethod = 'GET'
        )
        usertable = dynamodb.Table(USERTABLE)
        usertable.put_item(
            Item={
                'id': nextseq,
                'username': username,
                'email': email,
                'accepted_at': decimal.Decimal(str(now)),
                'host': host,
                'url': url
            }
        )
        
        mailbody = """
{0}様
ご登録ありがとうございました。
下記のURLからダウンロードできます。
{1}
""".format(username, url)
        send_email(email, "ご登録ありがとうございました", mailbody)
        
        return json.dumps({})
    except:
        import traceback
        err = traceback.format_exc()
        print(err)
        
        return {
            'statusCode': 500,
            'headers': {
                'context-type': 'text/json'
            },
            'body': json.dumps({
                'error': '内部エラーが発生しました'
            })
        }