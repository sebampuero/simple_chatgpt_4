#!/bin/bash
if ! command -v aws &> /dev/null; then
    echo "aws-cli needs to be installed"
    exit 1
fi
# Prompt for the first table name
read -p "Enter the name for the first table (chats_table): " first_table_name
first_table_name=${first_table_name:-chats_table}

# Prompt for the second table name
read -p "Enter the name for the second table (users_table): " second_table_name
second_table_name=${second_table_name:-users_table}

# Create the first table (chats_table)
aws dynamodb create-table \
    --table-name "$first_table_name" \
    --attribute-definitions \
        AttributeName=chat_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
        AttributeName=user_email,AttributeType=S \
    --key-schema \
        AttributeName=chat_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --global-secondary-indexes \
        '[
            {
                "IndexName": "user_email-index",
                "KeySchema": [{"AttributeName":"user_email","KeyType":"HASH"}],
                "Projection": {"ProjectionType":"ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }
        ]' \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5

# Create the second table (users_table)
aws dynamodb create-table \
    --table-name "$second_table_name" \
    --attribute-definitions \
        AttributeName=email,AttributeType=S \
    --key-schema \
        AttributeName=email,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5

echo "Tables $first_table_name and $second_table_name created successfully."