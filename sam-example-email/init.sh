if [ $# != 1 ]; then
  echo 引数エラー（メールアドレスを１つだけ指定すること）: $*
  exit 1
fi

MAILADDRESS=$1
aws dynamodb put-item --table-name mailaddress --item '{"email":{"S":"'$MAILADDRESS'"},"username":{"S":"山田太郎"},"haserror":{"N":"0"},"issend":{"N":"0"}}'
aws dynamodb put-item --table-name mailaddress --item '{"email":{"S":"success@simulator.amazonses.com"},"username":{"S":"秋山登"},"haserror":{"N":"0"},"issend":{"N":"0"}}'
aws dynamodb put-item --table-name mailaddress --item '{"email":{"S":"bounce@simulator.amazonses.com"},"username":{"S":"鈴木次郎"},"haserror":{"N":"0"},"issend":{"N":"0"}}'
aws dynamodb put-item --table-name mailaddress --item '{"email":{"S":"ooto@simulator.amazonses.com"},"username":{"S":"田中三郎"},"haserror":{"N":"0"},"issend":{"N":"0"}}'
aws dynamodb put-item --table-name mailaddress --item '{"email":{"S":"complaint@simulator.amazonses.com"},"username":{"S":"加藤四郎"},"haserror":{"N":"0"},"issend":{"N":"0"}}'
aws dynamodb put-item --table-name mailaddress --item '{"email":{"S":"suppressionlist@simulator.amazonses.com"},"username":{"S":"佐藤五郎"},"haserror":{"N":"0"},"issend":{"N":"0"}}'

TOPICARN=`aws cloudformation describe-stacks --stack-name "stack-sam-example-email" --query "Stacks[0].Outputs[?OutputKey=='BounceTopicArn'].OutputValue" --output text`
aws ses set-identity-notification-topic --identity $MAILADDRESS --notification-type Bounce --sns-topic $TOPICARN
aws s3 cp mail/mail.txt s3://mail-body-00001234-naoki