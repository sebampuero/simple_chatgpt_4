#!/bin/bash

# Prompt for authorized_users table name
read -p "Enter the authorized_users table name: " table_name

# Store that value in a variable
AUTHORIZED_TABLE_NAME=$table_name

# Ask for the new email that will be added
read -p "Enter the new email to be added: " new_email

# Store that also in a variable
NEW_EMAIL=$new_email

# Call an AWS command to put a new item in the authorized_users table with the stored email
aws dynamodb put-item \
    --table-name "$AUTHORIZED_TABLE_NAME" \
    --item '{
        "email": {"S": "'"$NEW_EMAIL"'"}
    }'

echo "Email $NEW_EMAIL has been added to the $AUTHORIZED_TABLE_NAME table."