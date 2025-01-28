#!/bin/bash
awslocal s3 mb s3://${S3_BUCKET_NAME} && \
awslocal dynamodb create-table --table-name=${DYNAMODB_TABLE_NAME} --key-schema AttributeName=id,KeyType=HASH --attribute-definitions AttributeName=id,AttributeType=S --billing-mode PAY_PER_REQUEST --region ${AWS_DEFAULT_REGION}
