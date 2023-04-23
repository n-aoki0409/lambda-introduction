S3_BUCKETNAME=`aws cloudformation describe-stacks --stack-name "sam-example-apigw" --query "Stacks[0].Outputs[?OutputKey=='MyFormBucketName'].OutputValue" --output text`
aws s3 sync html s3://$S3_BUCKETNAME

SEQUENCE_TABLENAME=`aws cloudformation describe-stacks --stack-name "sam-example-apigw" --query "Stacks[0].Outputs[?OutputKey=='MySequenceTableName'].OutputValue" --output text`
USER_TABLENAME=`aws cloudformation describe-stacks --stack-name "sam-example-apigw" --query "Stacks[0].Outputs[?OutputKey=='MyUserTableName'].OutputValue" --output text`
aws dynamodb put-item --table-name $SEQUENCE_TABLENAME --item '{"tablename":{"S":"'$USER_TABLENAME'"}, "seq":{"N":"0"}}'
aws s3 cp lambda.png s3://contents-00001234-naoki