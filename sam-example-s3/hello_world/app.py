import json
import boto3
import tempfile
import os
import pyminizip

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    tmpdir = tempfile.TemporaryDirectory()
    for rec in event['Records']:
        filename = rec['s3']['object']['key']
        bucketname = rec['s3']['bucket']['name']

        obj = s3.Object(bucketname, filename)
        response = obj.get()
        localfilename = os.path.join(tmpdir.name, filename)
        fp = open(localfilename, 'wb')
        fp.write(response['Body'].read())
        fp.close()

        zipfilename = tempfile.mkstemp(suffix='.zip')[1]
        os.chdir(tmpdir.name)
        pyminizip.compress(localfilename, None, zipfilename, 'mypassword', 0)

        destbucketname = os.environ['OUTPUTBUCKET']
        obj2 = s3.Object(destbucketname, filename + '.zip')
        response = obj2.put(
            Body=open(zipfilename, 'rb')
        )

        tmpdir.cleanup()